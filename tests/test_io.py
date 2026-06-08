"""Tests for I/O functionality."""

import json
import tempfile
from pathlib import Path

import pytest
from coda_bench.io import load_tasks, load_predictions, save_results
from coda_bench.schema import Task, Prediction


def test_load_tasks():
    """Test loading tasks from JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        tasks_data = [
            {
                "instance_id": 0,
                "question": "Test question",
                "answer": "Test answer",
                "answer_guidelines": "Guidelines",
                "reference_code": "print('test')",
                "dataset": "test-dataset",
                "notebook": "test-notebook",
                "release_community": "community_1"
            }
        ]
        json.dump(tasks_data, f)
        temp_path = f.name

    try:
        tasks = load_tasks(temp_path)
        assert len(tasks) == 1
        assert tasks[0].instance_id == 0
        assert tasks[0].question == "Test question"
    finally:
        Path(temp_path).unlink()


def test_load_predictions():
    """Test loading predictions from JSONL file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"instance_id": 0, "prediction": "answer 1"}\n')
        f.write('{"instance_id": 1, "prediction": "answer 2"}\n')
        temp_path = f.name

    try:
        predictions = load_predictions(temp_path)
        assert len(predictions) == 2
        assert predictions[0].instance_id == 0
        assert predictions[1].prediction == "answer 2"
    finally:
        Path(temp_path).unlink()


def test_save_results():
    """Test saving evaluation results."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        results = {
            "total": 10,
            "exact_matches": 7,
            "exact_accuracy": 0.7
        }
        save_results(results, temp_path)

        with open(temp_path) as f:
            loaded = json.load(f)

        assert loaded["total"] == 10
        assert loaded["exact_accuracy"] == 0.7
    finally:
        Path(temp_path).unlink()
