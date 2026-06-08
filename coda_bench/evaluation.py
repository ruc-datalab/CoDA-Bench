from __future__ import annotations

import re
from dataclasses import dataclass

from .schema import Prediction, Task


def normalize_answer(value: str) -> str:
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value.lower()


def numeric_tokens(value: str) -> list[float]:
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(value))
    return [float(x) for x in nums]


def exact_match(prediction: str, gold: str) -> bool:
    return normalize_answer(prediction) == normalize_answer(gold)


def numeric_match(prediction: str, gold: str, tol: float = 1e-6) -> bool:
    p_nums = numeric_tokens(prediction)
    g_nums = numeric_tokens(gold)
    if not p_nums or len(p_nums) != len(g_nums):
        return False
    return all(abs(p - g) <= tol for p, g in zip(p_nums, g_nums))


@dataclass
class EvaluationResult:
    n_gold: int
    n_pred: int
    n_scored: int
    exact_correct: int
    numeric_correct: int
    missing_ids: list[int]
    extra_ids: list[int]
    per_instance: list[dict]

    @property
    def exact_accuracy(self) -> float:
        return self.exact_correct / self.n_gold if self.n_gold else 0.0

    @property
    def numeric_accuracy(self) -> float:
        return self.numeric_correct / self.n_gold if self.n_gold else 0.0

    def to_dict(self) -> dict:
        return {
            "n_gold": self.n_gold,
            "n_pred": self.n_pred,
            "n_scored": self.n_scored,
            "exact_correct": self.exact_correct,
            "numeric_correct": self.numeric_correct,
            "exact_accuracy": self.exact_accuracy,
            "numeric_accuracy": self.numeric_accuracy,
            "missing_ids": self.missing_ids,
            "extra_ids": self.extra_ids,
            "per_instance": self.per_instance,
        }


def evaluate(tasks: list[Task], predictions: list[Prediction]) -> EvaluationResult:
    gold_by_id = {t.instance_id: t for t in tasks}
    pred_by_id = {p.instance_id: p for p in predictions}
    missing = sorted(set(gold_by_id) - set(pred_by_id))
    extra = sorted(set(pred_by_id) - set(gold_by_id))
    per_instance = []
    exact_correct = 0
    numeric_correct = 0
    for iid in sorted(set(gold_by_id) & set(pred_by_id)):
        task = gold_by_id[iid]
        pred = pred_by_id[iid]
        is_exact = exact_match(pred.prediction, task.answer)
        is_numeric = is_exact or numeric_match(pred.prediction, task.answer)
        exact_correct += int(is_exact)
        numeric_correct += int(is_numeric)
        per_instance.append({
            "instance_id": iid,
            "prediction": pred.prediction,
            "gold": task.answer,
            "exact_match": is_exact,
            "numeric_match": is_numeric,
            "release_community": task.release_community,
            "dataset": task.dataset,
        })
    return EvaluationResult(
        n_gold=len(tasks),
        n_pred=len(predictions),
        n_scored=len(per_instance),
        exact_correct=exact_correct,
        numeric_correct=numeric_correct,
        missing_ids=missing,
        extra_ids=extra,
        per_instance=per_instance,
    )
