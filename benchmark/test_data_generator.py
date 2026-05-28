#!/usr/bin/env python3
"""
Generate test datasets for Sorting benchmarks (TXT for Julia/C++/Python).
Sizes from BENCHMARK_SIZES (comma-separated), default 1e3 … 1e6 (incl. 2e4…8e4, 1e5…8e5).
"""

import json
import os
import random

NUM_DATASETS_PER_SIZE = 3
SEED = 42

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(ROOT, "test_data")


def _parse_sizes():
    raw = os.environ.get("BENCHMARK_SIZES", "").strip()
    if not raw:
        return [
            10**3,
            10**4,
            2 * 10**4,
            4 * 10**4,
            8 * 10**4,
            10**5,
            2 * 10**5,
            4 * 10**5,
            8 * 10**5,
            10**6,
        ]
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main():
    SIZES = _parse_sizes()
    os.makedirs(TEST_DATA_DIR, exist_ok=True)

    datasets = {"random": {}}

    for n in SIZES:
        for dataset_num in range(1, NUM_DATASETS_PER_SIZE + 1):
            random.seed(SEED + dataset_num)
            data = [random.randint(0, 1_000_000) for _ in range(n)]

            if dataset_num == 1:
                datasets["random"][str(n)] = data

            txt_path = os.path.join(TEST_DATA_DIR, f"data_{n}_{dataset_num}.txt")
            with open(txt_path, "w") as f:
                f.write(" ".join(map(str, data)))

        random.seed(SEED)
        data = [random.randint(0, 1_000_000) for _ in range(n)]
        txt_path = os.path.join(TEST_DATA_DIR, f"data_{n}.txt")
        with open(txt_path, "w") as f:
            f.write(" ".join(map(str, data)))

    json_path = os.path.join(TEST_DATA_DIR, "test_datasets.json")
    with open(json_path, "w") as f:
        json.dump(datasets, f)

    print(f"Wrote datasets for sizes {SIZES} to {TEST_DATA_DIR}")


if __name__ == "__main__":
    main()
