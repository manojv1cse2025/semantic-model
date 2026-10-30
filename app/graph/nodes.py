from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import text

from app.config import settings
from app.db.database import SessionLocal
from app.intent.classifier import IntentClassifier
from app.semantic.compiler import SQLCompiler
from app.semantic.models import SemanticQuery
from app.semantic.retrieval import SemanticRetrievalService


intent_classifier = IntentClassifier()
sql_compiler = SQLCompiler()


async def classify_intent(state):

    question = state["question"]

    intent = await intent_classifier.classify(
        question
    )

    return {
        "intent": intent
    }


async def retrieve_semantic_context(state):

    intent = state["intent"]
    workspace_id = state["workspace_id"]
    semantic_model_id = state["semantic_model_id"]
    question = state["question"]

    db = SessionLocal()

    try:
        retrieval_service = SemanticRetrievalService(db)

        context = retrieval_service.retrieve(
            semantic_model_id=semantic_model_id,
            workspace_id=workspace_id,
            intent=intent,
            question=question,
        )
    finally:
        db.close()

    return {
        "semantic_context": context
    }


async def build_semantic_query(state):

    question = state["question"]
    intent = state["intent"]
    context = state["semantic_context"]

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        google_api_key=settings.google_api_key,
        temperature=0
    )
    structured_llm = llm.with_structured_output(SemanticQuery)

    allowed_metrics = [m["name"] for m in context["metrics"]]
    allowed_dimensions = [d["name"] for d in context["dimensions"]]

    prompt = f"""
You are a semantic query planner.

User question:
{question}

Detected intent:
{intent.model_dump_json()}

You may ONLY use the following, already-validated fields:

Allowed metrics: {allowed_metrics}
Allowed dimensions: {allowed_dimensions}

Never invent a metric, dimension, table, or relationship that is not
listed above. If nothing matches, return empty lists.

Build a SemanticQuery describing exactly what to compute.
"""

    semantic_query = await structured_llm.ainvoke(prompt)

    return {
        "semantic_query": semantic_query
    }


def validate_semantic_query(state):

    query = state["semantic_query"]
    context = state["semantic_context"]

    errors = []

    allowed_metrics = {
        x["name"]
        for x in context["metrics"]
    }

    for metric in query.metrics:

        if metric not in allowed_metrics:
            errors.append(
                f"Unknown metric: {metric}"
            )

    allowed_dimensions = {
        x["name"]
        for x in context["dimensions"]
    }

    for dimension in query.dimensions:

        if dimension not in allowed_dimensions:
            errors.append(
                f"Unknown dimension: {dimension}"
            )

    return {
        "errors": errors
    }
    allowed_fields = allowed_dimensions | {"order_date"}  # or reuse allowed_dimensions once fix #1 is in
    for filt in query.filters:
        if filt.get("field") not in allowed_fields:
            errors.append(f"Unknown filter field: {filt.get('field')}")


def compile_sql(state):

    if state.get("errors"):
        return {}

    sql, params = sql_compiler.compile(
        state["semantic_query"], state["semantic_context"]
    )

    return {
        "sql": sql,
        "sql_params": params,
    }


def execute_sql(state):

    if state.get("errors") or not state.get("sql"):
        return {"result": None}

    db = SessionLocal()

    try:
        rows = db.execute(
            text(state["sql"]), state.get("sql_params", {})
        ).mappings().all()

        result = [dict(row) for row in rows]
    finally:
        db.close()

    return {
        "result": result
    }


async def generate_answer(state):

    if state.get("errors"):
        return {
            "answer": "I couldn't answer that: " + "; ".join(state["errors"])
        }

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        google_api_key=settings.google_api_key,
        temperature=0
    )

    prompt = f"""
User question:
{state['question']}

Query result (JSON rows):
{state.get('result')}

Write a concise, direct natural-language answer for a business user.
Do not mention SQL or databases.
"""

    response = await llm.ainvoke(prompt)

    return {
        "answer": response.content
    }
