from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    instance_id: int
    question: str
    answer: str
    answer_guidelines: str
    reference_code: str
    dataset: str
    notebook: str
    release_community: str
    data_path: str


class Prediction(BaseModel):
    instance_id: int
    prediction: str = Field(description="Final answer submitted by the agent")
    method: Optional[str] = None
    metadata: Optional[dict] = None
