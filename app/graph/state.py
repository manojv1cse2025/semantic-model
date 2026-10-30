from typing import TypedDict, Any


class GraphState(TypedDict, total=False):

    tenant_id: str

    workspace_id: str

    semantic_model_id: str

    question: str

    intent: Any

    semantic_context: Any

    semantic_query: Any

    sql: str

    sql_params: Any

    result: Any

    answer: str

    errors: list[str]
