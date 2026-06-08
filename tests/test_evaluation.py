"""Tests for evaluation functionality."""

import pytest
from coda_bench.evaluation import evaluate_prediction, EvaluationResult
from coda_bench.schema import Task, Prediction


def test_exact_match():
    """Test exact string matching."""
    task = Task(
        instance_id=0,
        question="What is the answer?",
        answer="42",
        answer_guidelines="Integer answer",
        reference_code="print(42)",
        dataset="test",
        notebook="test-notebook",
        release_community="community_1"
    )

    pred = Prediction(instance_id=0, prediction="42")
    result = evaluate_prediction(task, pred)

    assert result.exact_match is True
    assert result.numeric_match is True


def test_numeric_match():
    """Test numeric matching with tolerance."""
    task = Task(
        instance_id=1,
        question="What is the percentage?",
        answer="50.0%",
        answer_guidelines="Percentage",
        reference_code="print('50.0%')",
        dataset="test",
        notebook="test-notebook",
        release_community="community_1"
    )

    # Should match with different formatting
    pred = Prediction(instance_id=1, prediction="50%")
    result = evaluate_prediction(task, pred)

    assert result.numeric_match is True


def test_evaluation_result():
    """Test EvaluationResult aggregation."""
    result = EvaluationResult(
        total=10,
        exact_matches=7,
        numeric_matches=8,
        exact_accuracy=0.7,
        numeric_accuracy=0.8
    )

    assert result.total == 10
    assert result.exact_accuracy == 0.7
    assert result.numeric_accuracy == 0.8
