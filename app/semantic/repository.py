from sqlalchemy import text


class SemanticRepository:

    def __init__(self, db):
        self.db = db

    def find_metrics(
        self,
        semantic_model_id,
        names: list[str]
    ):

        if not names:
            return []

        query = text("""
            SELECT
                id,
                name,
                expression,
                aggregation,
                description,
                synonyms
            FROM metrics
            WHERE semantic_model_id = :model_id
              AND (
                    name = ANY(:names)
                    OR synonyms && :names
              )
        """)

        return self.db.execute(
            query,
            {
                "model_id": semantic_model_id,
                "names": names,
            }
        ).mappings().all()

    def find_dimensions(
        self,
        semantic_model_id,
        names: list[str]
    ):

        if not names:
            return []

        query = text("""
            SELECT
                id,
                entity_id,
                name,
                physical_column,
                data_type,
                description,
                synonyms
            FROM dimensions
            WHERE semantic_model_id = :model_id
              AND (
                    name = ANY(:names)
                    OR synonyms && :names
              )
        """)

        return self.db.execute(
            query,
            {
                "model_id": semantic_model_id,
                "names": names,
            }
        ).mappings().all()

    def find_entities(
        self,
        semantic_model_id,
        names: list[str] | None = None
    ):

        if names:
            query = text("""
                SELECT id, name, description, physical_table, primary_key
                FROM entities
                WHERE semantic_model_id = :model_id
                  AND name = ANY(:names)
            """)
            params = {"model_id": semantic_model_id, "names": names}
        else:
            query = text("""
                SELECT id, name, description, physical_table, primary_key
                FROM entities
                WHERE semantic_model_id = :model_id
            """)
            params = {"model_id": semantic_model_id}

        return self.db.execute(query, params).mappings().all()

    def find_entities_by_id(
        self,
        semantic_model_id,
        entity_ids: list
    ):

        if not entity_ids:
            return []

        query = text("""
            SELECT id, name, description, physical_table, primary_key
            FROM entities
            WHERE semantic_model_id = :model_id
              AND id = ANY(:entity_ids)
        """)

        return self.db.execute(
            query,
            {
                "model_id": semantic_model_id,
                "entity_ids": entity_ids,
            }
        ).mappings().all()

    def find_relationships(
        self,
        semantic_model_id,
        entity_ids: list | None = None
    ):

        if entity_ids:
            query = text("""
                SELECT id, from_entity_id, to_entity_id, relationship_type, join_sql
                FROM relationships
                WHERE semantic_model_id = :model_id
                  AND (
                        from_entity_id = ANY(:entity_ids)
                        OR to_entity_id = ANY(:entity_ids)
                  )
            """)
            params = {"model_id": semantic_model_id, "entity_ids": entity_ids}
        else:
            query = text("""
                SELECT id, from_entity_id, to_entity_id, relationship_type, join_sql
                FROM relationships
                WHERE semantic_model_id = :model_id
            """)
            params = {"model_id": semantic_model_id}

        return self.db.execute(query, params).mappings().all()

    def find_business_rules(
        self,
        semantic_model_id
    ):

        query = text("""
            SELECT id, name, rule, priority
            FROM business_rules
            WHERE semantic_model_id = :model_id
            ORDER BY priority ASC
        """)

        return self.db.execute(
            query,
            {"model_id": semantic_model_id}
        ).mappings().all()
