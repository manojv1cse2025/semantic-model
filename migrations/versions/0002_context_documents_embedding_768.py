"""alter context_documents embedding to vector(768)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-13

"""
from alembic import op


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP INDEX IF EXISTS context_documents_embedding_idx;")

    op.execute("""
        ALTER TABLE context_documents
        ALTER COLUMN embedding TYPE vector(768);
    """)

    op.execute("""
        CREATE INDEX context_documents_embedding_idx
        ON context_documents
        USING hnsw (embedding vector_cosine_ops);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS context_documents_embedding_idx;")

    op.execute("""
        ALTER TABLE context_documents
        ALTER COLUMN embedding TYPE vector(1536);
    """)

    op.execute("""
        CREATE INDEX context_documents_embedding_idx
        ON context_documents
        USING hnsw (embedding vector_cosine_ops);
    """)
