import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.context.service import embed_text
from app.db import models
from app.db.database import get_db
from app.graph.graph import build_graph


router = APIRouter()

_graph = build_graph()


def _serialize(obj) -> dict:
    return {
        column.name: getattr(obj, column.key if hasattr(column, "key") else column.name)
        for column in obj.__table__.columns
    }


# ---------- Schemas ----------

class TenantCreate(BaseModel):
    name: str


class WorkspaceCreate(BaseModel):
    tenant_id: uuid.UUID
    name: str


class SemanticModelCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str
    description: str | None = None


class EntityCreate(BaseModel):
    name: str
    description: str | None = None
    physical_table: str
    primary_key: str


class DimensionCreate(BaseModel):
    entity_id: uuid.UUID | None = None
    name: str
    physical_column: str
    data_type: str
    description: str | None = None
    synonyms: list[str] = []


class MetricCreate(BaseModel):
    name: str
    expression: str
    aggregation: str | None = None
    description: str | None = None
    synonyms: list[str] = []
    format: str | None = None


class RelationshipCreate(BaseModel):
    from_entity_id: uuid.UUID
    to_entity_id: uuid.UUID
    relationship_type: str
    join_sql: str


class BusinessRuleCreate(BaseModel):
    name: str
    rule: str
    priority: int = 100


class ContextDocumentCreate(BaseModel):
    document_type: str
    title: str
    content: str
    metadata: dict = {}


class QueryRequest(BaseModel):
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    semantic_model_id: uuid.UUID
    question: str


# ---------- Tenants / workspaces ----------

@router.post("/tenants")
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    tenant = models.Tenant(name=payload.name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return _serialize(tenant)


@router.post("/workspaces")
def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)):
    workspace = models.Workspace(**payload.model_dump())
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return _serialize(workspace)


# ---------- Semantic models ----------

@router.post("/semantic-models")
def create_semantic_model(payload: SemanticModelCreate, db: Session = Depends(get_db)):
    semantic_model = models.SemanticModel(**payload.model_dump())
    db.add(semantic_model)
    db.commit()
    db.refresh(semantic_model)
    return _serialize(semantic_model)


@router.get("/semantic-models/{semantic_model_id}")
def get_semantic_model(semantic_model_id: uuid.UUID, db: Session = Depends(get_db)):
    semantic_model = db.get(models.SemanticModel, semantic_model_id)

    if not semantic_model:
        raise HTTPException(status_code=404, detail="Semantic model not found")

    return _serialize(semantic_model)


@router.post("/semantic-models/{semantic_model_id}/entities")
def create_entity(semantic_model_id: uuid.UUID, payload: EntityCreate, db: Session = Depends(get_db)):
    entity = models.Entity(semantic_model_id=semantic_model_id, **payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return _serialize(entity)


@router.post("/semantic-models/{semantic_model_id}/dimensions")
def create_dimension(semantic_model_id: uuid.UUID, payload: DimensionCreate, db: Session = Depends(get_db)):
    dimension = models.Dimension(semantic_model_id=semantic_model_id, **payload.model_dump())
    db.add(dimension)
    db.commit()
    db.refresh(dimension)
    return _serialize(dimension)


@router.post("/semantic-models/{semantic_model_id}/metrics")
def create_metric(semantic_model_id: uuid.UUID, payload: MetricCreate, db: Session = Depends(get_db)):
    metric = models.Metric(semantic_model_id=semantic_model_id, **payload.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return _serialize(metric)


@router.post("/semantic-models/{semantic_model_id}/relationships")
def create_relationship(semantic_model_id: uuid.UUID, payload: RelationshipCreate, db: Session = Depends(get_db)):
    relationship = models.Relationship(semantic_model_id=semantic_model_id, **payload.model_dump())
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return _serialize(relationship)


@router.post("/semantic-models/{semantic_model_id}/business-rules")
def create_business_rule(semantic_model_id: uuid.UUID, payload: BusinessRuleCreate, db: Session = Depends(get_db)):
    rule = models.BusinessRule(semantic_model_id=semantic_model_id, **payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _serialize(rule)


# ---------- Context documents ----------

@router.post("/workspaces/{workspace_id}/context-documents")
def create_context_document(workspace_id: uuid.UUID, payload: ContextDocumentCreate, db: Session = Depends(get_db)):
    embedding = embed_text(payload.content)

    document = models.ContextDocument(
        workspace_id=workspace_id,
        document_type=payload.document_type,
        title=payload.title,
        content=payload.content,
        metadata_=payload.metadata,
        embedding=embedding,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    data = _serialize(document)
    data.pop("embedding", None)
    return data


# ---------- Query ----------

@router.post("/query")
async def run_query(payload: QueryRequest):
    result = await _graph.ainvoke({
        "tenant_id": str(payload.tenant_id),
        "workspace_id": str(payload.workspace_id),
        "semantic_model_id": str(payload.semantic_model_id),
        "question": payload.question,
    })

    return {
        "answer": result.get("answer"),
        "sql": result.get("sql"),
        "result": result.get("result"),
        "errors": result.get("errors", []),
    }
