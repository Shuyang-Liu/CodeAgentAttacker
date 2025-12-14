import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

MODEL = "gpt-5-mini"
VANILLA_RUN = Path(__file__).parent.parent.parent/"outputs"/"swebench"/MODEL
RUN_ID = 2
SAMPLES_ID_PATH = Path(__file__).parent.parent/"sample-data"/"samples"/"general"/f"{RUN_ID}"/"sampled_instances.json"
ATTACK_RUN = Path(__file__).parent.parent.parent/"outputs"/"attack"/"swebench"/MODEL/f"run-{RUN_ID}"
FIGURE_DIR = Path(__file__).parent.parent.parent/"figures"

if not FIGURE_DIR.exists():
    FIGURE_DIR.mkdir(parents=True)

def load_samples():
    with open(SAMPLES_ID_PATH, 'r', encoding='utf-8') as f:
        return [sample['instance_id'] for sample in json.load(f)]

def get_trajectory_lengths(instance_ids, run_dir):
    lengths = []
    for instance_id in instance_ids:
        traj_path = run_dir / instance_id / f"{instance_id}.traj.json"
        if traj_path.exists():
            with open(traj_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                api_calls = data.get("info", {}).get("model_stats", {}).get("api_calls", 0)
                lengths.append(api_calls)
                if api_calls == 0:
                    print(f"Warning: Zero API calls for instance {instance_id} in run {run_dir}")
    return lengths

def get_attack_stats(instance_ids):
    stats = {
        'total_observations': [],
        'python_observations': [],
        'text_observations': [],
        'ast_operators_applied': [],
        'text_perturbation_applied': []
    }

    for instance_id in instance_ids:
        attack_path = ATTACK_RUN / instance_id / f"{instance_id}.attack.json"
        if attack_path.exists():
            with open(attack_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                info = data.get("info", {})
                for key in stats.keys():
                    stats[key].append(info.get(key, 0))

    return stats

def plot_trajectory_comparison(vanilla_lengths, attack_lengths):
    plt.rcParams.update({'font.size': 20})

    fig, ax = plt.subplots(1, 1, figsize=(5, 5))

    # Calculate statistics for both datasets
    def calc_outliers(data, q1, q3):
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        return [x for x in data if x < lower_fence or x > upper_fence]

    vanilla_q1 = np.percentile(vanilla_lengths, 25)
    vanilla_median = np.median(vanilla_lengths)
    vanilla_q3 = np.percentile(vanilla_lengths, 75)
    vanilla_outliers = calc_outliers(vanilla_lengths, vanilla_q1, vanilla_q3)
    vanilla_iqr = vanilla_q3 - vanilla_q1
    vanilla_lower_whisker = max(np.min(vanilla_lengths), vanilla_q1 - 1.5 * vanilla_iqr)
    vanilla_upper_whisker = min(np.max(vanilla_lengths), vanilla_q3 + 1.5 * vanilla_iqr)

    attack_q1 = np.percentile(attack_lengths, 25)
    attack_median = np.median(attack_lengths)
    attack_q3 = np.percentile(attack_lengths, 75)
    attack_outliers = calc_outliers(attack_lengths, attack_q1, attack_q3)
    attack_iqr = attack_q3 - attack_q1
    attack_lower_whisker = max(np.min(attack_lengths), attack_q1 - 1.5 * attack_iqr)
    attack_upper_whisker = min(np.max(attack_lengths), attack_q3 + 1.5 * attack_iqr)

    # Plot settings
    categories = ['Vanilla', 'Attack']
    x_pos = [0, 1]
    bar_width = 0.4
    colors = ['#1f77b4', '#ff7f0e']  # Blue and orange

    for i, (q1, median, q3, lower_w, upper_w, outliers, color) in enumerate([
        (vanilla_q1, vanilla_median, vanilla_q3, vanilla_lower_whisker, vanilla_upper_whisker, vanilla_outliers, colors[0]),
        (attack_q1, attack_median, attack_q3, attack_lower_whisker, attack_upper_whisker, attack_outliers, colors[1])
    ]):
        # Draw whiskers
        ax.plot([x_pos[i], x_pos[i]], [lower_w, q1], color=color, linewidth=1.5)
        ax.plot([x_pos[i], x_pos[i]], [q3, upper_w], color=color, linewidth=1.5)
        # Draw IQR rectangle
        ax.bar(x_pos[i], q3 - q1, bar_width, bottom=q1,
               color=color, alpha=0.3, edgecolor=color, linewidth=1.5)
        # Draw median line
        ax.plot([x_pos[i] - bar_width/2, x_pos[i] + bar_width/2],
                [median, median], color=color, linewidth=2.5)
        # Draw whisker caps
        ax.plot([x_pos[i] - bar_width/4, x_pos[i] + bar_width/4],
                [lower_w, lower_w], color=color, linewidth=1.5)
        ax.plot([x_pos[i] - bar_width/4, x_pos[i] + bar_width/4],
                [upper_w, upper_w], color=color, linewidth=1.5)
        # Draw outliers
        if outliers:
            ax.scatter([x_pos[i]] * len(outliers), outliers,
                      color=color, s=30, alpha=0.6, zorder=3)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories)
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylabel('API Calls (Trajectory Length)')
    ax.set_title('Trajectory Length Distribution')
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = FIGURE_DIR / f'trajectory_comparison_run_{RUN_ID}.pdf'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Trajectory comparison saved to: {output_path}")
    plt.close()

def plot_attack_distribution(attack_stats):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    metrics = [
        ('total_observations', 'Total Observations per Instance'),
        ('text_perturbation_applied', 'Text Perturbations Applied'),
        ('ast_operators_applied', 'AST Operators Applied'),
        ('text_observations', 'Text Observations')
    ]

    for idx, (key, title) in enumerate(metrics):
        row, col = idx // 2, idx % 2
        data = attack_stats[key]
        if data:
            axes[row, col].hist(data, bins=20, color='orange', edgecolor='black', alpha=0.7)
            axes[row, col].set_xlabel('Count')
            axes[row, col].set_ylabel('Frequency')
            axes[row, col].set_title(title)
            axes[row, col].grid(alpha=0.3)

    plt.tight_layout()
    output_path = FIGURE_DIR / f'attack_distribution_run_{RUN_ID}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Attack distribution saved to: {output_path}")
    plt.close()

if __name__ == "__main__":
    instance_ids = load_samples()

    vanilla_lengths = get_trajectory_lengths(instance_ids, VANILLA_RUN)
    attack_lengths = get_trajectory_lengths(instance_ids, ATTACK_RUN)

    print(f"{'='*80}")
    print(f"Trajectory Length Statistics (Model: {MODEL}, Run ID: {RUN_ID})")
    print(f"{'='*80}")
    print(f"Vanilla - Mean: {np.mean(vanilla_lengths):.2f}, Median: {np.median(vanilla_lengths):.2f}, Std: {np.std(vanilla_lengths):.2f}")
    print(f"Attack  - Mean: {np.mean(attack_lengths):.2f}, Median: {np.median(attack_lengths):.2f}, Std: {np.std(attack_lengths):.2f}")
    print(f"Difference - Mean: {np.mean(attack_lengths) - np.mean(vanilla_lengths):.2f}")

    plot_trajectory_comparison(vanilla_lengths, attack_lengths)

    # attack_stats = get_attack_stats(instance_ids)

    # print(f"\n{'='*80}")
    # print(f"Attack Statistics")
    # print(f"{'='*80}")
    # for key, values in attack_stats.items():
    #     if values:
    #         print(f"{key}: Mean={np.mean(values):.2f}, Median={np.median(values):.2f}, Max={np.max(values)}")

    # plot_attack_distribution(attack_stats)