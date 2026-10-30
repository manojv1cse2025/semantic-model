"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-06

"""
from alembic import op


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.execute("""
        CREATE TABLE tenants (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE workspaces (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE semantic_models (
            id UUID PRIMARY KEY,
            workspace_id UUID NOT NULL REFERENCES workspaces(id),
            name TEXT NOT NULL,
            description TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE entities (
            id UUID PRIMARY KEY,
            semantic_model_id UUID NOT NULL REFERENCES semantic_models(id),
            name TEXT NOT NULL,
            description TEXT,
            physical_table TEXT NOT NULL,
            primary_key TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE dimensions (
            id UUID PRIMARY KEY,
            semantic_model_id UUID NOT NULL REFERENCES semantic_models(id),
            entity_id UUID REFERENCES entities(id),
            name TEXT NOT NULL,
            physical_column TEXT NOT NULL,
            data_type TEXT NOT NULL,
            description TEXT,
            synonyms TEXT[],
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE metrics (
            id UUID PRIMARY KEY,
            semantic_model_id UUID NOT NULL REFERENCES semantic_models(id),
            name TEXT NOT NULL,
            expression TEXT NOT NULL,
            aggregation TEXT,
            description TEXT,
            synonyms TEXT[],
            format TEXT,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE relationships (
            id UUID PRIMARY KEY,
            semantic_model_id UUID NOT NULL REFERENCES semantic_models(id),
            from_entity_id UUID NOT NULL REFERENCES entities(id),
            to_entity_id UUID NOT NULL REFERENCES entities(id),
            relationship_type TEXT NOT NULL,
            join_sql TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE business_rules (
            id UUID PRIMARY KEY,
            semantic_model_id UUID NOT NULL REFERENCES semantic_models(id),
            name TEXT NOT NULL,
            rule TEXT NOT NULL,
            priority INTEGER DEFAULT 100,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE context_documents (
            id UUID PRIMARY KEY,
            workspace_id UUID NOT NULL REFERENCES workspaces(id),
            document_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            embedding vector(1536),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE INDEX context_documents_embedding_idx
        ON context_documents
        USING hnsw (embedding vector_cosine_ops);
    """)

    op.execute("""
        CREATE TABLE customers (
            customer_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price NUMERIC(12, 2) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
            product_id INTEGER NOT NULL REFERENCES products(product_id),
            amount NUMERIC(12, 2) NOT NULL,
            status TEXT NOT NULL DEFAULT 'COMPLETED',
            order_date TIMESTAMPTZ DEFAULT now()
        );
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS orders;")
    op.execute("DROP TABLE IF EXISTS products;")
    op.execute("DROP TABLE IF EXISTS customers;")
    op.execute("DROP TABLE IF EXISTS context_documents;")
    op.execute("DROP TABLE IF EXISTS business_rules;")
    op.execute("DROP TABLE IF EXISTS relationships;")
    op.execute("DROP TABLE IF EXISTS metrics;")
    op.execute("DROP TABLE IF EXISTS dimensions;")
    op.execute("DROP TABLE IF EXISTS entities;")
    op.execute("DROP TABLE IF EXISTS semantic_models;")
    op.execute("DROP TABLE IF EXISTS workspaces;")
    op.execute("DROP TABLE IF EXISTS tenants;")
