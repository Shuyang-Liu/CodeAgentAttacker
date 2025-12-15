# CodeAgentAttacker

This is the artifact of **WHEN ENVIRONMENTS MISLEAD: EXFILTRATION AND OBSERVATION ATTACKS AGAINST CODING AGENTS**.

## Overview

This repository implements **observation perturbation attacks** against coding agents by corrupting command outputs to test agent robustness under adversarial conditions.

## Core Components
### Data Exfiltration
We host the implementation of the two attacks under `data_exfiltration`.

### Bug Injection (`bug_injection/`)

- **`bug_injector.py`**: Main API with `inject_bugs()` function
  - Auto-detects Python code vs. shell output
  - AST-based mutations for code (16 operators: arithmetic, comparison, control flow, etc.)
  - Text perturbations for output (line deletion, reordering, truncation, noise)

### Agent Integration (`mini-swe-agent/`)

- Modified SWE-agent with attack hooks
- Enable via config: `enable_attack: true`
- Intercepts and perturbs observations before agent consumption
- Logs all transformations to `.attack.json`

## Setup

```bash
pip install -e .
cd mini-swe-agent && pip install -e .
```

## Usage

**Direct API:**
```python
from bug_injection.bug_injector import inject_bugs
perturbed, ops = inject_bugs(code, max_operators=3, seed=42)
```

**Run Attack:**
```bash
./mini-swe-agent/script/sample_inject.sh <RUN_ID>
./mini-swe-agent/script/eval_sample_inject.sh <RUN_ID>
```

**Analyze:**
```bash
python mini-swe-agent/script/misc/compare_w_wo_attack_traj.py
python mini-swe-agent/script/misc/compare_w_wo_attack_resolution.py
```

## Results

- **`figures/`**: Analysis visualizations (trajectory comparison, resolution heatmaps)
- **`mini-swe-agent/outputs/`**: Attack trajectories (`.traj.json`), predictions, and perturbation logs (`.attack.json`)
