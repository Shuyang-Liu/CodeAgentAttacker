import random
from typing import List

NOISE_POOL = [
    "[warning] unexpected output",
    "note: partial output truncated",
    "debug: retrying operation",
    "info: continuing execution",
    "[info] processing...",
    "# additional context omitted",
    "** output may be incomplete **",
    "all tests passed successfully",
    "error: minor issue encountered",
]


def transform_non_code_text(
    text: str,
    seed: int = None,
    delete_prob: float = 0.25,
    reorder_prob: float = 0.2,
    noise_prob: float = 0.3,
    truncate_prob: float = 0.15,
    strip_whitespace: bool = True,
    strip_blank_lines: bool = True,
) -> str:
    """
    Corruption for non-code observations:
      - strip blank/whitespace-only lines
      - random line deletion
      - line truncation
      - local reordering
      - multiple noise injection

    Designed to preserve overall structure while simulating noisy tooling.
    """

    if seed is not None:
        random.seed(seed)

    lines = text.splitlines()
    if not lines:
        return text

    if strip_blank_lines:
        lines = [line for line in lines if line.strip()]

    if not lines:
        return ""

    # --- 1. Random deletion ---
    filtered = []
    for line in lines:
        if random.random() > delete_prob:
            filtered.append(line)

    if not filtered:
        filtered = lines[:1]

    # --- 2. Line truncation ---
    for i in range(len(filtered)):
        if len(filtered[i]) > 40 and random.random() < truncate_prob:
            cutoff = random.randint(20, len(filtered[i]) - 5)
            filtered[i] = filtered[i][:cutoff] + "..."

    # --- 3. Local reordering ---
    i = 0
    while i < len(filtered) - 1:
        if random.random() < reorder_prob:
            filtered[i], filtered[i+1] = filtered[i+1], filtered[i]
            i += 2
        else:
            i += 1

    # --- 4. Multiple noise injection ---
    num_noise = 0
    if random.random() < noise_prob:
        num_noise = random.randint(1, 3)

    for _ in range(num_noise):
        noise_line = random.choice(NOISE_POOL)
        insert_pos = random.randint(0, len(filtered))
        filtered.insert(insert_pos, noise_line)

    if strip_whitespace:
        filtered = [line.strip() for line in filtered]

    return "\n".join(filtered)
