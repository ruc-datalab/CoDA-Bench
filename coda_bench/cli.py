from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from .evaluation import evaluate
from .io import load_predictions, load_tasks, write_json


def evaluate_app(
    pred: Path = typer.Option(..., "--pred", help="JSONL file with {instance_id, prediction}"),
    gold: Path = typer.Option(..., "--gold", help="CODA-BENCH task JSON file"),
    out: Optional[Path] = typer.Option(None, "--out", help="Optional JSON result path"),
):
    result = evaluate(load_tasks(gold), load_predictions(pred)).to_dict()
    summary = {k: v for k, v in result.items() if k not in {"per_instance", "missing_ids", "extra_ids"}}
    summary["missing_count"] = len(result["missing_ids"])
    summary["extra_count"] = len(result["extra_ids"])
    print(summary)
    if out:
        write_json(out, result)


def validate_app(
    pred: Path = typer.Option(..., "--pred"),
    gold: Path = typer.Option(..., "--gold"),
):
    tasks = load_tasks(gold)
    preds = load_predictions(pred)
    gold_ids = {t.instance_id for t in tasks}
    pred_ids = [p.instance_id for p in preds]
    duplicates = sorted({x for x in pred_ids if pred_ids.count(x) > 1})
    extra = sorted(set(pred_ids) - gold_ids)
    missing = sorted(gold_ids - set(pred_ids))
    ok = not duplicates and not extra
    print({"ok": ok, "n_predictions": len(preds), "duplicates": duplicates, "extra_ids": extra, "missing_count": len(missing)})
    raise typer.Exit(0 if ok else 1)


def evaluate_main():
    typer.run(evaluate_app)


def validate_main():
    typer.run(validate_app)
