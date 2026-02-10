import csv
from typing import Dict, List


def extract_column_samples(csv_path: str, sample_size: int = 3) -> Dict[str, List[str]]:
    samples = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col, val in row.items():
                samples.setdefault(col, [])
                if val and len(samples[col]) < sample_size:
                    samples[col].append(val)

    return samples
