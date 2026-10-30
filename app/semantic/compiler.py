import re


class SQLCompiler:
    """Deterministically compiles a validated SemanticQuery + semantic
    context (metrics/dimensions/entities/relationships/business_rules
    already resolved from Postgres) into physical SQL. The LLM never
    sees or produces this SQL directly."""

    def compile(self, semantic_query, context):

        metrics_by_name = {m["name"]: m for m in context["metrics"]}
        dimensions_by_name = {d["name"]: d for d in context["dimensions"]}
        entities_by_id = {e["id"]: e for e in context["entities"]}

        select_parts = []
        group_by_parts = []
        required_tables = set()

        for dim_name in semantic_query.dimensions:
            dimension = dimensions_by_name.get(dim_name)

            if not dimension:
                raise ValueError(f"Unknown dimension: {dim_name}")

            column = dimension["physical_column"]
            select_parts.append(f"{column} AS {dim_name}")
            group_by_parts.append(column)
            required_tables.add(self._table_from_column(column))

        for metric_name in semantic_query.metrics:
            metric = metrics_by_name.get(metric_name)

            if not metric:
                raise ValueError(f"Unknown metric: {metric_name}")

            expression = metric["expression"]
            select_parts.append(f"{expression} AS {metric_name}")
            required_tables.update(self._tables_from_expression(expression))

        if not select_parts:
            raise ValueError("Semantic query has no metrics or dimensions")

        where_parts = []
        params = {}

        for index, filt in enumerate(semantic_query.filters):
            field = filt["field"]
            operator = filt["operator"]
            value = filt["value"]

            dimension = dimensions_by_name.get(field)
            column = dimension["physical_column"] if dimension else field

            required_tables.add(self._table_from_column(column))

            param_name = f"filter_{index}"
            where_parts.append(f"{column} {operator} :{param_name}")
            params[param_name] = value

        base_table, join_clauses, joined_tables = self._build_joins(
            required_tables, context["relationships"], entities_by_id
        )

        for rule in context["business_rules"]:
            rule_tables = self._tables_from_expression(rule["rule"])

            if rule_tables.issubset(joined_tables):
                where_parts.append(f"({rule['rule']})")

        sql = "SELECT\n    " + ",\n    ".join(select_parts)
        sql += f"\nFROM {base_table}"

        for join_clause in join_clauses:
            sql += f"\n{join_clause}"

        if where_parts:
            sql += "\nWHERE " + "\n  AND ".join(where_parts)

        if group_by_parts:
            sql += "\nGROUP BY " + ", ".join(group_by_parts)

        if semantic_query.order_by:
            order_terms = [
                f"{o['field']} {o.get('direction', 'ASC')}"
                for o in semantic_query.order_by
            ]
            sql += "\nORDER BY " + ", ".join(order_terms)

        sql += f"\nLIMIT {semantic_query.limit};"

        return sql, params

    @staticmethod
    def _table_from_column(column: str) -> str:
        return column.split(".")[0]

    @staticmethod
    def _tables_from_expression(expression: str) -> set[str]:
        return set(re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\.[a-zA-Z_]", expression))

    @staticmethod
    def _build_joins(required_tables, relationships, entities_by_id):

        table_by_entity_id = {
            entity_id: entity["physical_table"]
            for entity_id, entity in entities_by_id.items()
        }

        edges = []
        for rel in relationships:
            from_table = table_by_entity_id.get(rel["from_entity_id"])
            to_table = table_by_entity_id.get(rel["to_entity_id"])

            if from_table and to_table:
                edges.append((from_table, to_table, rel["join_sql"]))

        remaining = set(required_tables)

        if not remaining:
            raise ValueError("No tables resolved for this query")

        base_table = sorted(remaining)[0]
        joined = {base_table}
        remaining.discard(base_table)

        join_clauses = []

        while remaining:
            progressed = False

            for from_table, to_table, join_sql in edges:
                if from_table in joined and to_table in remaining:
                    join_clauses.append(f"JOIN {to_table} ON {join_sql}")
                    joined.add(to_table)
                    remaining.discard(to_table)
                    progressed = True

                elif to_table in joined and from_table in remaining:
                    join_clauses.append(f"JOIN {from_table} ON {join_sql}")
                    joined.add(from_table)
                    remaining.discard(from_table)
                    progressed = True

            if not progressed:
                raise ValueError(
                    f"No relationship path found to join tables: {remaining}"
                )

        return base_table, join_clauses, joined
