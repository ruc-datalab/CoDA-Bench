from __future__ import annotations

import json
from pathlib import Path

from .schema import Prediction, Task


def load_tasks(path: str | Path) -> list[Task]:
    with open(path, "r", encoding="utf-8") as f:
        return [Task.model_validate(row) for row in json.load(f)]


def load_predictions(path: str | Path) -> list[Prediction]:
    preds: list[Prediction] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                preds.append(Prediction.model_validate_json(line))
            except Exception as exc:  # pragma: no cover - CLI path
                raise ValueError(f"Invalid JSONL prediction at line {line_no}: {exc}") from exc
    return preds


def write_json(path: str | Path, obj: object) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")
