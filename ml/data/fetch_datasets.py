from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


DATASETS = {
    "APTOS2019": {
        "type": "kaggle_competition",
        "id": "aptos2019-blindness-detection",
        "target": "data/raw/APTOS2019",
    },
    "RFMiD": {
        "type": "manual",
        "target": "data/raw/RFMiD",
        "url": "https://ieee-dataport.org/open-access/retinal-fundus-multi-disease-image-dataset-rfmid",
    },
    "DIARETDB1": {
        "type": "manual",
        "target": "data/raw/DIARETDB1",
        "url": "https://www.it.lut.fi/project/imageret/diaretdb1/",
    },
    "MESSIDOR2": {
        "type": "manual",
        "target": "data/raw/MESSIDOR2",
        "url": "https://www.adcis.net/en/third-party/messidor2/",
    },
    "ORIGA": {
        "type": "manual",
        "target": "data/raw/ORIGA",
        "url": "https://imed.nimte.ac.cn/ORIGA-dataset/",
    },
    "DRIVE": {
        "type": "manual",
        "target": "data/raw/DRIVE",
        "url": "https://drive.grand-challenge.org/",
    },
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def download_kaggle_competition(comp_id: str, target: str) -> None:
    ensure_dir(target)
    run(["kaggle", "competitions", "download", "-c", comp_id, "-p", target])


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch available RetinalAI datasets")
    parser.add_argument("--dataset", choices=list(DATASETS.keys()) + ["all"], default="all")
    args = parser.parse_args()

    selected = DATASETS.keys() if args.dataset == "all" else [args.dataset]

    for name in selected:
        meta = DATASETS[name]
        ensure_dir(meta["target"])

        if meta["type"] == "kaggle_competition":
            if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
                print(f"Downloading {name} via Kaggle API...")
                try:
                    download_kaggle_competition(meta["id"], meta["target"])
                except Exception as exc:
                    print(f"Failed to download {name}: {exc}")
            else:
                print(f"Skipping {name}: Kaggle credentials not set.")
        else:
            print(f"Manual download required for {name}.")
            print(f"Source: {meta['url']}")
            print(f"Place files in: {meta['target']}")


if __name__ == "__main__":
    main()
