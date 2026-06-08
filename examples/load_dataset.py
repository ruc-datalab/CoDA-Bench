"""Load and inspect CoDA-Bench dataset.

Usage:
    python examples/load_dataset.py
    python examples/load_dataset.py --split hard --limit 5
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_dataset(dataset_path: Path) -> list[dict]:
    """Load dataset from JSON file."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_task_summary(task: dict, idx: int) -> None:
    """Print a summary of a single task."""
    print(f"\n{'='*80}")
    print(f"Task #{idx} (instance_id: {task['instance_id']})")
    print(f"{'='*80}")
    print(f"\n📋 Question:")
    print(f"   {task['question']}")
    print(f"\n✅ Answer:")
    print(f"   {task['answer']}")
    print(f"\n📝 Answer Guidelines:")
    print(f"   {task['answer_guidelines']}")
    print(f"\n📊 Metadata:")
    print(f"   Dataset: {task['dataset']}")
    print(f"   Notebook: {task['notebook']}")
    print(f"   Community: {task['release_community']}")
    print(f"\n💻 Reference Code (first 200 chars):")
    code_preview = task['reference_code'][:200].replace('\n', '\n   ')
    print(f"   {code_preview}...")


def main():
    parser = argparse.ArgumentParser(description="Load and inspect CoDA-Bench dataset")
    parser.add_argument(
        "--split",
        type=str,
        choices=["full", "hard"],
        default="full",
        help="Dataset split to load (full or hard)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of tasks to display",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing dataset files",
    )
    args = parser.parse_args()

    # Determine dataset file
    if args.split == "full":
        dataset_file = args.data_dir / "coda_bench.json"
    else:
        dataset_file = args.data_dir / "coda_bench_hard.json"

    if not dataset_file.exists():
        print(f"❌ Error: Dataset file not found: {dataset_file}")
        print(f"   Please download the dataset from HuggingFace first.")
        return

    # Load dataset
    print(f"Loading {args.split} dataset from {dataset_file}...")
    tasks = load_dataset(dataset_file)

    print(f"\n{'='*80}")
    print(f"📊 Dataset Statistics")
    print(f"{'='*80}")
    print(f"Total tasks: {len(tasks)}")
    print(f"Split: {args.split.upper()}")

    # Count communities
    communities = set(task['release_community'] for task in tasks)
    print(f"Communities: {len(communities)}")

    # Count datasets
    datasets = set(task['dataset'] for task in tasks)
    print(f"Unique datasets: {len(datasets)}")

    # Display sample tasks
    print(f"\n{'='*80}")
    print(f"Sample Tasks (showing {min(args.limit, len(tasks))} of {len(tasks)})")
    print(f"{'='*80}")

    for idx, task in enumerate(tasks[:args.limit], 1):
        print_task_summary(task, idx)

    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
