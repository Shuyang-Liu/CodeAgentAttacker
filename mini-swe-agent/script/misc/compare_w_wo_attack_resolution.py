import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

MODEL = "gpt-5-mini"
FULL_REPORT_PATH = Path(__file__).parent.parent.parent/"outputs"/"swebench"/MODEL/"sb-cli-reports"/"swe-bench_verified__test__gpt-5-mini-v1-1-1.json"
RUN_ID = 2
SAMPLES_ID_PATH = Path(__file__).parent.parent/"sample-data"/"samples"/"general"/f"{RUN_ID}"/"sampled_instances.json"
ATTACK_REPORT_PATH = Path(__file__).parent.parent/f"openai__{MODEL}.{RUN_ID}.json"
FIGURE_DIR = Path(__file__).parent.parent.parent/"figures"

if not FIGURE_DIR.exists():
    FIGURE_DIR.mkdir(parents=True)

def get_resolution_status(report_path):
    with open(SAMPLES_ID_PATH, 'r', encoding='utf-8') as f:
        samples_data = json.load(f)

    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    resolved_ids = set(report_data.get('resolved_ids', []))
    return {sample['instance_id']: sample['instance_id'] in resolved_ids
            for sample in samples_data}


def create_heatmap(before_status, after_status):
    plt.rcParams.update({'font.size': 20})

    resolved_to_unresolved = [
        iid for iid in before_status
        if before_status[iid] and not after_status.get(iid, False)
    ]

    matrix = np.array([
        [sum(before_status[i] and after_status.get(i, False) for i in before_status),
         sum(before_status[i] and not after_status.get(i, False) for i in before_status)],
        [sum(not before_status[i] and after_status.get(i, False) for i in before_status),
         sum(not before_status[i] and not after_status.get(i, False) for i in before_status)]
    ])

    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Resolved', 'Unresolved'],
                yticklabels=['Resolved', 'Unresolved'],
                cbar_kws={'label': 'Count'})
    plt.xlabel('After Attack')
    plt.ylabel('Before Attack')
    plt.title('Resolution Status Transition Heatmap')
    plt.tight_layout()

    output_path = FIGURE_DIR / f'heatmap_run_{RUN_ID}.pdf'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nHeatmap saved to: {output_path}")
    plt.close()

    return resolved_to_unresolved

if __name__ == "__main__":
    before_status = get_resolution_status(FULL_REPORT_PATH)
    after_status = get_resolution_status(ATTACK_REPORT_PATH)

    vanilla_rate = sum(before_status.values()) / len(before_status) if before_status else 0
    attacked_rate = sum(after_status.values()) / len(after_status) if after_status else 0

    print(f"Vanilla Resolution Rate (Model {MODEL}, Run {RUN_ID}): {vanilla_rate:.2%}")
    print(f"Attacked Resolution Rate (Model {MODEL}, Run {RUN_ID}): {attacked_rate:.2%}")

    resolved_to_unresolved = create_heatmap(before_status, after_status)

    print(f"\n{'='*80}")
    print(f"Resolved → Unresolved ({len(resolved_to_unresolved)} instances):")
    print(f"{'='*80}")
    for instance_id in resolved_to_unresolved:
        print(instance_id)
        