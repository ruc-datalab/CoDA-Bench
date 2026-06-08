#!/usr/bin/env python3
"""Quick test script to verify CoDA-Bench installation and evaluation."""

import json
import tempfile
from pathlib import Path

# Test 1: Import modules
print("Test 1: Importing modules...")
from coda_bench.schema import Task, Prediction
from coda_bench.evaluation import evaluate
from coda_bench.io import load_tasks, load_predictions
print("✓ All imports successful")

# Test 2: Create sample data
print("\nTest 2: Creating sample data...")
sample_tasks = [
    {
        "instance_id": 0,
        "question": "What is 2+2?",
        "answer": "4",
        "answer_guidelines": "Integer answer",
        "reference_code": "print(2+2)",
        "dataset": "test",
        "notebook": "test-nb",
        "release_community": "community_1",
        "data_path": "/tmp/test"
    },
    {
        "instance_id": 1,
        "question": "What percentage is 50/100?",
        "answer": "50%",
        "answer_guidelines": "Percentage",
        "reference_code": "print('50%')",
        "dataset": "test",
        "notebook": "test-nb",
        "release_community": "community_1",
        "data_path": "/tmp/test"
    }
]

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(sample_tasks, f)
    tasks_file = f.name

sample_predictions = [
    {"instance_id": 0, "prediction": "4"},
    {"instance_id": 1, "prediction": "50%"}
]

with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
    for pred in sample_predictions:
        f.write(json.dumps(pred) + '\n')
    preds_file = f.name

print(f"✓ Created tasks file: {tasks_file}")
print(f"✓ Created predictions file: {preds_file}")

# Test 3: Load data
print("\nTest 3: Loading data...")
tasks = load_tasks(tasks_file)
preds = load_predictions(preds_file)
print(f"✓ Loaded {len(tasks)} tasks")
print(f"✓ Loaded {len(preds)} predictions")

# Test 4: Evaluate
print("\nTest 4: Running evaluation...")
result = evaluate(tasks, preds)
print(f"✓ Evaluation completed")
print(f"  - Gold tasks: {result.n_gold}")
print(f"  - Predictions: {result.n_pred}")
print(f"  - Exact correct: {result.exact_correct}")
print(f"  - Exact accuracy: {result.exact_accuracy:.2%}")
print(f"  - Numeric accuracy: {result.numeric_accuracy:.2%}")

# Cleanup
Path(tasks_file).unlink()
Path(preds_file).unlink()

print("\n" + "="*50)
print("All tests passed! ✓")
print("="*50)
