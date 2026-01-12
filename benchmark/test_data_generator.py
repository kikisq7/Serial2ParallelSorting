#!/usr/bin/env python3
"""
Generate test datasets for benchmarks (JSON for Python; TXT for Julia/C++).
"""

import json
import os
import random

# SIZES = [10**7, 10**8]
SIZES = [10**4]
NUM_DATASETS_PER_SIZE = 3  # Generate 3 different datasets per size
SEED = 42

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(ROOT, "test_data")

def main():
    os.makedirs(TEST_DATA_DIR, exist_ok=True)

    datasets = {
        "random": {},
    }

    for n in SIZES:
        # Generate multiple datasets for each size
        for dataset_num in range(1, NUM_DATASETS_PER_SIZE + 1):
            # Use different seed for each dataset to ensure different data
            random.seed(SEED + dataset_num)
            data = [random.randint(0, 1_000_000) for _ in range(n)]
            
            # Store in JSON (using first dataset as default)
            if dataset_num == 1:
                datasets["random"][str(n)] = data

            # Write plain text files for Julia/C++ (space-separated single line)
            txt_path = os.path.join(TEST_DATA_DIR, f"data_{n}_{dataset_num}.txt")
            with open(txt_path, "w") as f:
                f.write(" ".join(map(str, data)))
        
        # Also create the default data_{n}.txt for backward compatibility
        random.seed(SEED)
        data = [random.randint(0, 1_000_000) for _ in range(n)]
        txt_path = os.path.join(TEST_DATA_DIR, f"data_{n}.txt")
        with open(txt_path, "w") as f:
            f.write(" ".join(map(str, data)))

    # Write JSON for Python benchmark compatibility
    json_path = os.path.join(TEST_DATA_DIR, "test_datasets.json")
    with open(json_path, "w") as f:
        json.dump(datasets, f)

    print(f"Wrote datasets to {TEST_DATA_DIR}")

if __name__ == "__main__":
    main()


