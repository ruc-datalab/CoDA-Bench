#!/usr/bin/env python3
"""
CoDA-Bench OpenHands Evaluation Runner (Docker Mode)

Evaluates agents on CoDA-Bench using secure Docker isolation.

Usage:
    python scripts/run_evaluation.py --model gpt-5.5 --output results/run1

    # With specific instances
    python scripts/run_evaluation.py --model gpt-5.5 --instances 0 1 2 --output results/test

    # Full evaluation
    python scripts/run_evaluation.py --model gpt-5.5 --output results/full --workers 8
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import threading

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = REPO_ROOT / "datasets" / "coda_bench.json"
DEFAULT_DATA_ROOT = REPO_ROOT / "datasets" / "communities"
DOCKER_SCRIPT = REPO_ROOT / "docker" / "openhands" / "run_task.sh"


class EvaluationRunner:
    def __init__(self, model: str, dataset_path: Path, data_root: Path,
                 output_dir: Path, workers: int, timeout: int,
                 start_idx: int, end_idx: int, instance_ids: list):
        self.model = model
        self.dataset_path = dataset_path
        self.data_root = data_root
        self.output_dir = output_dir
        self.workers = workers
        self.timeout = timeout
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.instance_ids = instance_ids

        self.lock = threading.Lock()
        self.stats = {"success": 0, "failed": 0, "skipped": 0}

        # Load dataset
        with open(self.dataset_path) as f:
            all_tasks = json.load(f)

        # Filter tasks
        if instance_ids:
            self.tasks = [t for t in all_tasks if t["instance_id"] in instance_ids]
        else:
            end = end_idx if end_idx is not None else len(all_tasks)
            self.tasks = all_tasks[start_idx:end]

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        with self.lock:
            print(f"[{ts}] {msg}", flush=True)

    def check_environment(self):
        """Check if required environment variables are set."""
        required = ["LLM_API_KEY"]
        missing = [var for var in required if not os.environ.get(var)]

        if missing:
            self.log(f"ERROR: Missing environment variables: {', '.join(missing)}")
            sys.exit(1)

        # Check Docker script exists
        if not DOCKER_SCRIPT.exists():
            self.log(f"ERROR: Docker script not found: {DOCKER_SCRIPT}")
            sys.exit(1)

    def prepare_task(self, task: dict, workspace_dir: Path):
        """Prepare task description file."""
        workspace_dir.mkdir(parents=True, exist_ok=True)

        prompt = (
            f"You are a data analyst. Answer the following question by analyzing "
            f"the data available in /data directory.\n\n"
            f"The data directory contains community datasets with CSV files in "
            f"subdirectories. Explore /data to find relevant files.\n\n"
            f"Question: {task['question']}\n\n"
            f"{task.get('answer_guidelines', '')}\n\n"
            f"Write your final answer to /workspace/result.txt (just the answer, nothing else)."
        )

        (workspace_dir / "task_description.txt").write_text(prompt, encoding="utf-8")

    def run_single_instance(self, task: dict) -> dict:
        """Run a single task instance using Docker."""
        iid = task["instance_id"]
        inst_dir = self.output_dir / f"instance_{iid}"
        workspace_dir = inst_dir / "workspace"
        output_dir = inst_dir / "output"

        # Get community data path
        community = task.get("release_community", "")
        data_path = self.data_root / community / "full_community"

        if not data_path.exists():
            self.log(f"[{iid}] SKIPPED: Data not found at {data_path}")
            with self.lock:
                self.stats["skipped"] += 1
            return {
                "instance_id": iid,
                "status": "skipped",
                "reason": "data_not_found"
            }

        # Prepare task
        self.prepare_task(task, workspace_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run Docker task
        self.log(f"[{iid}] Starting...")
        start_time = time.time()

        try:
            env = os.environ.copy()
            env["LLM_MODEL"] = env.get("LLM_MODEL", self.model)

            result = subprocess.run([
                "bash",
                str(DOCKER_SCRIPT),
                str(workspace_dir.resolve()),
                str(data_path.resolve()),
                str(output_dir.resolve())
            ], capture_output=True, text=True, timeout=self.timeout + 60, env=env)

            duration = time.time() - start_time

            # Check result
            result_file = workspace_dir / "result.txt"
            if result_file.exists():
                prediction = result_file.read_text(encoding="utf-8").strip()
                status = "success" if prediction else "failed"
            else:
                prediction = ""
                status = "failed"

            success = bool(prediction) and status == "success"

            with self.lock:
                if success:
                    self.stats["success"] += 1
                else:
                    self.stats["failed"] += 1

            pred_preview = prediction[:60] + ("..." if len(prediction) > 60 else "")
            self.log(f"[{iid}] {status.upper()} in {duration:.1f}s | pred={pred_preview!r} | "
                    f"OK={self.stats['success']} FAIL={self.stats['failed']}")

            return {
                "instance_id": iid,
                "status": status,
                "prediction": prediction,
                "duration": duration
            }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            with self.lock:
                self.stats["failed"] += 1
            self.log(f"[{iid}] TIMEOUT after {duration:.1f}s")
            return {
                "instance_id": iid,
                "status": "timeout",
                "duration": duration
            }
        except Exception as e:
            duration = time.time() - start_time
            with self.lock:
                self.stats["failed"] += 1
            self.log(f"[{iid}] ERROR: {e}")
            return {
                "instance_id": iid,
                "status": "error",
                "error": str(e),
                "duration": duration
            }

    def run(self):
        """Run evaluation on all tasks."""
        self.log("="*60)
        self.log("CoDA-Bench Evaluation - OpenHands (Docker Mode)")
        self.log("="*60)
        self.log(f"Model: {self.model}")
        self.log(f"Dataset: {self.dataset_path}")
        self.log(f"Data root: {self.data_root}")
        self.log(f"Output: {self.output_dir}")
        self.log(f"Tasks: {len(self.tasks)}")
        self.log(f"Workers: {self.workers}")
        self.log(f"Timeout: {self.timeout}s")
        self.log("="*60)

        # Check environment
        self.check_environment()

        # Run tasks
        results = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.run_single_instance, task): task
                      for task in self.tasks}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    task = futures[future]
                    self.log(f"[{task['instance_id']}] EXCEPTION: {e}")
                    results.append({
                        "instance_id": task["instance_id"],
                        "status": "exception",
                        "error": str(e)
                    })
                    with self.lock:
                        self.stats["failed"] += 1

        total_time = time.time() - start_time

        # Save summary
        summary = {
            "agent": "openhands",
            "model": self.model,
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "total_time": total_time,
            "stats": self.stats,
            "results": sorted(results, key=lambda r: r["instance_id"])
        }

        summary_file = self.output_dir / "evaluation_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        # Generate predictions file for scoring
        predictions_file = self.output_dir / "predictions.jsonl"
        with open(predictions_file, "w") as f:
            for result in sorted(results, key=lambda r: r["instance_id"]):
                if result.get("prediction"):
                    f.write(json.dumps({
                        "instance_id": result["instance_id"],
                        "prediction": result["prediction"]
                    }) + "\n")

        self.log("="*60)
        self.log(f"Evaluation Complete!")
        self.log(f"Time: {total_time:.1f}s")
        self.log(f"Success: {self.stats['success']}")
        self.log(f"Failed: {self.stats['failed']}")
        self.log(f"Skipped: {self.stats['skipped']}")
        self.log(f"Summary: {summary_file}")
        self.log(f"Predictions: {predictions_file}")
        self.log("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Run CoDA-Bench evaluation with OpenHands in Docker"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model name (e.g., gpt-5.5, claude-opus-4-7)"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to dataset JSON file"
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help="Root directory containing community data"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for results"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout per instance in seconds"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index (inclusive)"
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="End index (exclusive)"
    )
    parser.add_argument(
        "--instances",
        type=int,
        nargs="*",
        help="Specific instance IDs to run"
    )

    args = parser.parse_args()

    # Set model env var
    os.environ["LLM_MODEL"] = args.model

    runner = EvaluationRunner(
        model=args.model,
        dataset_path=args.dataset,
        data_root=args.data_root,
        output_dir=args.output,
        workers=args.workers,
        timeout=args.timeout,
        start_idx=args.start,
        end_idx=args.end,
        instance_ids=args.instances
    )

    runner.run()


if __name__ == "__main__":
    main()
