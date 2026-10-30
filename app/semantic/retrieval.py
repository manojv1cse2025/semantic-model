from app.context.service import ContextService, embed_text
from app.semantic.repository import SemanticRepository


class SemanticRetrievalService:

    def __init__(self, db):
        self.db = db
        self.repository = SemanticRepository(db)
        self.context_service = ContextService(db)

    def retrieve(self, semantic_model_id, workspace_id, intent, question: str):

        metrics = self.repository.find_metrics(semantic_model_id, intent.metrics)
        dimensions = self.repository.find_dimensions(semantic_model_id, intent.dimensions)

        entities = self.repository.find_entities(
            semantic_model_id, intent.entities or None
        )

        known_entity_ids = {e["id"] for e in entities}
        dimension_entity_ids = {d["entity_id"] for d in dimensions if d["entity_id"]}
        missing_entity_ids = list(dimension_entity_ids - known_entity_ids)

        if missing_entity_ids:
            entities = list(entities) + list(
                self.repository.find_entities_by_id(semantic_model_id, missing_entity_ids)
            )

        entity_ids = [e["id"] for e in entities]

        relationships = self.repository.find_relationships(semantic_model_id, entity_ids)
        business_rules = self.repository.find_business_rules(semantic_model_id)

        try:
            embedding = embed_text(question)
            documents = self.context_service.retrieve(workspace_id, embedding)
        except Exception:
            documents = []

        return {
            "metrics": [dict(m) for m in metrics],
            "dimensions": [dict(d) for d in dimensions],
            "entities": [dict(e) for e in entities],
            "relationships": [dict(r) for r in relationships],
            "business_rules": [dict(b) for b in business_rules],
            "documents": [dict(doc) for doc in documents],
        }
