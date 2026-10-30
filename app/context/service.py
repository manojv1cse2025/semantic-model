from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy import text

from app.config import settings


def embed_text(text_to_embed: str) -> list[float]:
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key
    )
    return embeddings.embed_query(text_to_embed)


class ContextService:

    def __init__(self, db):
        self.db = db

    def retrieve(
        self,
        workspace_id,
        embedding,
        limit=8
    ):

        query = text("""
            SELECT
                id,
                title,
                document_type,
                content,
                metadata,

                1 - (
                    embedding <=> CAST(:embedding AS vector)
                ) AS similarity

            FROM context_documents

            WHERE workspace_id = :workspace_id

            ORDER BY
                embedding <=> CAST(:embedding AS vector)

            LIMIT :limit
        """)

        return self.db.execute(
            query,
            {
                "workspace_id": workspace_id,
                "embedding": str(embedding),
                "limit": limit,
            }
        ).mappings().all()
