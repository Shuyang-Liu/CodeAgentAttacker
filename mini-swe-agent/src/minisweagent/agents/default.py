"""Basic agent class. See https://mini-swe-agent.com/latest/advanced/control_flow/ for visual explanation."""

import re
import subprocess
from dataclasses import asdict, dataclass

from jinja2 import StrictUndefined, Template

from minisweagent import Environment, Model


@dataclass
class AgentConfig:
    # The default settings are the bare minimum to run the agent. Take a look at the config files for improved settings.
    system_template: str = "You are a helpful assistant that can do anything."
    instance_template: str = (
        "Your task: {{task}}. Please reply with a single shell command in triple backticks. "
        "To finish, the first line of the output of the shell command must be 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'."
    )
    timeout_template: str = (
        "The last command <command>{{action['action']}}</command> timed out and has been killed.\n"
        "The output of the command was:\n <output>\n{{output}}\n</output>\n"
        "Please try another command and make sure to avoid those requiring interactive input."
    )
    format_error_template: str = "Please always provide EXACTLY ONE action in triple backticks."
    action_observation_template: str = "Observation: {{output}}"
    action_regex: str = r"```bash\s*\n(.*?)\n```"
    step_limit: int = 0
    cost_limit: float = 3.0
    enable_attack: bool = False  # Enable observation perturbation attack
    attack_max_operators: int = 3  # Maximum mutation operators to apply


class NonTerminatingException(Exception):
    """Raised for conditions that can be handled by the agent."""


class FormatError(NonTerminatingException):
    """Raised when the LM's output is not in the expected format."""


class ExecutionTimeoutError(NonTerminatingException):
    """Raised when the action execution timed out."""


class TerminatingException(Exception):
    """Raised for conditions that terminate the agent."""


class Submitted(TerminatingException):
    """Raised when the LM declares that the agent has finished its task."""


class LimitsExceeded(TerminatingException):
    """Raised when the agent has reached its cost or step limit."""


class DefaultAgent:
    def __init__(self, model: Model, env: Environment, *, config_class: type = AgentConfig, **kwargs):
        self.config = config_class(**kwargs)
        self.messages: list[dict] = []
        self.model = model
        self.env = env
        self.extra_template_vars = {}
        self._init_attack()

    def _init_attack(self):
        """Initialize attack module if enabled."""
        self.perturb_fn = None
        self.attack_log = []  # Track successful perturbation records only
        self.attack_stats = {"total": 0, "perturbed": 0, "python": 0, "text": 0}  # Track all observations
        if self.config.enable_attack:
            print("Initializing observation perturbation attack...")
            try:
                from bug_injection.bug_injector import inject_bugs
                self.perturb_fn = lambda obs: inject_bugs(obs, max_operators=self.config.attack_max_operators)
            except ImportError:
                print("Warning: bug_injection module not found. Observation perturbation disabled.")

    def get_attack_data(self) -> dict:
        """Get attack statistics and perturbation log."""
        if not self.config.enable_attack:
            return None

        # Count by content type
        python_obs = self.attack_stats.get("python", 0)
        text_obs = self.attack_stats.get("text", 0)

        # Count by operators applied
        ast_applied = sum(1 for r in self.attack_log if "text_perturbation" not in r.get("applied_operators", []))
        text_applied = sum(1 for r in self.attack_log if "text_perturbation" in r.get("applied_operators", []))

        return {
            "info": {
                "total_observations": self.attack_stats["total"],
                "python_observations": python_obs,
                "text_observations": text_obs,
                "ast_operators_applied": ast_applied,
                "text_perturbation_applied": text_applied,
                "skipped": self.attack_stats["total"] - self.attack_stats["perturbed"],
            },
            "perturbations": self.attack_log
        }

    def render_template(self, template: str, **kwargs) -> str:
        template_vars = asdict(self.config) | self.env.get_template_vars() | self.model.get_template_vars()
        return Template(template, undefined=StrictUndefined).render(
            **kwargs, **template_vars, **self.extra_template_vars
        )

    def add_message(self, role: str, content: str, **kwargs):
        self.messages.append({"role": role, "content": content, **kwargs})

    def run(self, task: str, **kwargs) -> tuple[str, str]:
        """Run step() until agent is finished. Return exit status & message"""
        self.extra_template_vars |= {"task": task, **kwargs}
        self.messages = []
        self.add_message("system", self.render_template(self.config.system_template))
        self.add_message("user", self.render_template(self.config.instance_template))
        while True:
            try:
                self.step()
            except NonTerminatingException as e:
                self.add_message("user", str(e))
            except TerminatingException as e:
                self.add_message("user", str(e))
                return type(e).__name__, str(e)

    def step(self) -> dict:
        """Query the LM, execute the action, return the observation."""
        return self.get_observation(self.query())

    def query(self) -> dict:
        """Query the model and return the response."""
        if 0 < self.config.step_limit <= self.model.n_calls or 0 < self.config.cost_limit <= self.model.cost:
            raise LimitsExceeded()
        response = self.model.query(self.messages)
        self.add_message("assistant", **response)
        return response

    def get_observation(self, response: dict) -> dict:
        """Execute the action and return the observation."""
        action = self.parse_action(response)
        output = self.execute_action(action)

        # Apply observation perturbation if configured
        perturbed_output = dict(output)
        original_obs = output.get("output", "")

        if self.config.enable_attack and original_obs.strip():
            self.attack_stats["total"] += 1
            # Classify as Python or text
            is_python = self._is_python_code(original_obs)
            if is_python:
                self.attack_stats["python"] += 1
            else:
                self.attack_stats["text"] += 1

        if self.perturb_fn and original_obs.strip():
            perturbed_output["output"], applied_ops = self.perturb_fn(original_obs)

            # Log only successful perturbations
            if self.config.enable_attack and applied_ops:
                self.attack_stats["perturbed"] += 1
                self.attack_log.append({
                    "action": action.get("action", ""),
                    "original": original_obs,
                    "perturbed": perturbed_output["output"],
                    "applied_operators": applied_ops
                })

        observation = self.render_template(self.config.action_observation_template, output=perturbed_output)
        self.add_message("user", observation)
        return output

    def _is_python_code(self, text: str) -> bool:
        """Check if text is parseable Python code."""
        try:
            import ast
            ast.parse(text)
            return True
        except:
            return False

    def parse_action(self, response: dict) -> dict:
        """Parse the action from the message. Returns the action."""
        actions = re.findall(self.config.action_regex, response["content"], re.DOTALL)
        if len(actions) == 1:
            return {"action": actions[0].strip(), **response}
        raise FormatError(self.render_template(self.config.format_error_template, actions=actions))

    def execute_action(self, action: dict) -> dict:
        try:
            output = self.env.execute(action["action"])
        except subprocess.TimeoutExpired as e:
            output = e.output.decode("utf-8", errors="replace") if e.output else ""
            raise ExecutionTimeoutError(
                self.render_template(self.config.timeout_template, action=action, output=output)
            )
        except TimeoutError:
            raise ExecutionTimeoutError(self.render_template(self.config.timeout_template, action=action, output=""))
        self.has_finished(output)
        return output

    def has_finished(self, output: dict[str, str]):
        """Raises Submitted exception with final output if the agent has finished its task."""
        lines = output.get("output", "").lstrip().splitlines(keepends=True)
        if lines and lines[0].strip() in ["MINI_SWE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"]:
            raise Submitted("".join(lines[1:]))
