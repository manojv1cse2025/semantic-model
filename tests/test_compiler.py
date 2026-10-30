from app.semantic.compiler import SQLCompiler
from app.semantic.models import SemanticQuery


def _context():
    customer_id = "11111111-1111-1111-1111-111111111111"
    order_id = "22222222-2222-2222-2222-222222222222"

    return {
        "metrics": [
            {"name": "revenue", "expression": "SUM(orders.amount)"},
        ],
        "dimensions": [
            {
                "name": "customer_country",
                "physical_column": "customers.country",
                "entity_id": customer_id,
            },
        ],
        "entities": [
            {"id": customer_id, "physical_table": "customers"},
            {"id": order_id, "physical_table": "orders"},
        ],
        "relationships": [
            {
                "from_entity_id": order_id,
                "to_entity_id": customer_id,
                "join_sql": "orders.customer_id = customers.customer_id",
            },
        ],
        "business_rules": [
            {"name": "valid_revenue", "rule": "orders.status NOT IN ('CANCELLED', 'REFUNDED')"},
            {"name": "unrelated_rule", "rule": "products.category = 'Electronics'"},
        ],
    }


def test_compile_revenue_by_country():
    query = SemanticQuery(metrics=["revenue"], dimensions=["customer_country"])

    sql, params = SQLCompiler().compile(query, _context())

    assert "SUM(orders.amount) AS revenue" in sql
    assert "customers.country AS customer_country" in sql
    assert "JOIN orders" in sql or "JOIN customers" in sql
    assert "GROUP BY customers.country" in sql
    assert "orders.status NOT IN" in sql
    assert "products.category" not in sql
    assert params == {}


def test_compile_unknown_metric_raises():
    query = SemanticQuery(metrics=["made_up_metric"])

    try:
        SQLCompiler().compile(query, _context())
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "made_up_metric" in str(exc)
