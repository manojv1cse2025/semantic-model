from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.graph.state import GraphState
from app.graph.nodes import (
    classify_intent,
    retrieve_semantic_context,
    build_semantic_query,
    validate_semantic_query,
    compile_sql,
    execute_sql,
    generate_answer,
)


def build_graph():

    graph = StateGraph(GraphState)

    graph.add_node(
        "intent",
        classify_intent
    )

    graph.add_node(
        "retrieve_context",
        retrieve_semantic_context
    )

    graph.add_node(
        "build_query",
        build_semantic_query
    )

    graph.add_node(
        "validate",
        validate_semantic_query
    )

    graph.add_node(
        "compile_sql",
        compile_sql
    )

    graph.add_node(
        "execute",
        execute_sql
    )

    graph.add_node(
        "answer",
        generate_answer
    )

    graph.add_edge(
        START,
        "intent"
    )

    graph.add_edge(
        "intent",
        "retrieve_context"
    )

    graph.add_edge(
        "retrieve_context",
        "build_query"
    )

    graph.add_edge(
        "build_query",
        "validate"
    )

    graph.add_edge(
        "validate",
        "compile_sql"
    )

    graph.add_edge(
        "compile_sql",
        "execute"
    )

    graph.add_edge(
        "execute",
        "answer"
    )

    graph.add_edge(
        "answer",
        END
    )

    return graph.compile()
