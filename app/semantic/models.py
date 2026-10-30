from pydantic import BaseModel, Field


class SemanticQuery(BaseModel):

    metrics: list[str] = Field(
        default_factory=list
    )

    dimensions: list[str] = Field(
        default_factory=list
    )

    filters: list[dict] = Field(
        default_factory=list
    )

    time_dimension: str | None = None

    time_grain: str | None = None

    order_by: list[dict] = Field(
        default_factory=list
    )

    limit: int = 100
