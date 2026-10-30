from typing import Literal

from pydantic import BaseModel, Field


class UserIntent(BaseModel):

    intent: Literal[
        "metric_query",
        "comparison",
        "trend",
        "breakdown",
        "definition",
        "data_exploration",
        "unknown",
    ]

    metrics: list[str] = Field(default_factory=list)

    dimensions: list[str] = Field(default_factory=list)

    entities: list[str] = Field(default_factory=list)

    filters: dict = Field(default_factory=dict)

    time_range: str | None = None

    time_grain: str | None = None

    confidence: float = 0.0
