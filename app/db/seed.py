from app.db.database import SessionLocal
from app.db import models


def run():
    db = SessionLocal()

    try:
        tenant = models.Tenant(name="Demo Tenant")
        db.add(tenant)
        db.flush()

        workspace = models.Workspace(tenant_id=tenant.id, name="Demo Workspace")
        db.add(workspace)
        db.flush()

        semantic_model = models.SemanticModel(
            workspace_id=workspace.id,
            name="ecommerce",
            description="Customers, orders and products semantic model",
            status="published",
        )
        db.add(semantic_model)
        db.flush()

        customer_entity = models.Entity(
            semantic_model_id=semantic_model.id,
            name="customer",
            description="A customer who places orders",
            physical_table="customers",
            primary_key="customer_id",
        )

        order_entity = models.Entity(
            semantic_model_id=semantic_model.id,
            name="order",
            description="An order placed by a customer",
            physical_table="orders",
            primary_key="order_id",
        )

        product_entity = models.Entity(
            semantic_model_id=semantic_model.id,
            name="product",
            description="A product that can be ordered",
            physical_table="products",
            primary_key="product_id",
        )

        db.add_all([customer_entity, order_entity, product_entity])
        db.flush()

        dimensions = [
            models.Dimension(
                semantic_model_id=semantic_model.id,
                entity_id=customer_entity.id,
                name="customer_country",
                physical_column="customers.country",
                data_type="text",
                description="The country a customer is based in",
                synonyms=["country", "customer country", "geography"],
            ),
            models.Dimension(
                semantic_model_id=semantic_model.id,
                entity_id=order_entity.id,
                name="order_status",
                physical_column="orders.status",
                data_type="text",
                description="The status of an order",
                synonyms=["status", "order status"],
            ),
            models.Dimension(
                semantic_model_id=semantic_model.id,
                entity_id=product_entity.id,
                name="product_category",
                physical_column="products.category",
                data_type="text",
                description="The category a product belongs to",
                synonyms=["category", "product category"],
            ),
        ]
        db.add_all(dimensions)

        metrics = [
            models.Metric(
                semantic_model_id=semantic_model.id,
                name="revenue",
                expression="SUM(orders.amount)",
                aggregation="sum",
                description="Total revenue from valid orders",
                synonyms=["sales", "income", "total sales", "revenue"],
                format="currency",
            ),
            models.Metric(
                semantic_model_id=semantic_model.id,
                name="order_count",
                expression="COUNT(DISTINCT orders.order_id)",
                aggregation="count",
                description="Number of orders placed",
                synonyms=["orders", "number of orders", "order volume"],
                format="number",
            ),
        ]
        db.add_all(metrics)

        db.add(models.Relationship(
            semantic_model_id=semantic_model.id,
            from_entity_id=order_entity.id,
            to_entity_id=customer_entity.id,
            relationship_type="many_to_one",
            join_sql="orders.customer_id = customers.customer_id",
        ))

        db.add(models.Relationship(
            semantic_model_id=semantic_model.id,
            from_entity_id=order_entity.id,
            to_entity_id=product_entity.id,
            relationship_type="many_to_one",
            join_sql="orders.product_id = products.product_id",
        ))

        business_rules = [
            models.BusinessRule(
                semantic_model_id=semantic_model.id,
                name="valid_revenue",
                rule="orders.status NOT IN ('CANCELLED', 'REFUNDED')",
                priority=100,
            ),
            models.BusinessRule(
                semantic_model_id=semantic_model.id,
                name="active_customer",
                rule="customers.status = 'ACTIVE'",
                priority=200,
            ),
        ]
        db.add_all(business_rules)

        customers = [
            models.Customer(name="Aria Mendes", country="Brazil"),
            models.Customer(name="Liam Chen", country="Canada"),
            models.Customer(name="Noor Haddad", country="UAE"),
            models.Customer(name="Sofia Rossi", country="Italy"),
        ]
        db.add_all(customers)
        db.flush()

        products = [
            models.Product(name="Wireless Mouse", category="Electronics", price=25.00),
            models.Product(name="Standing Desk", category="Furniture", price=350.00),
            models.Product(name="Noise Cancelling Headphones", category="Electronics", price=180.00),
        ]
        db.add_all(products)
        db.flush()

        orders = [
            models.Order(customer_id=customers[0].customer_id, product_id=products[0].product_id, amount=25.00, status="COMPLETED"),
            models.Order(customer_id=customers[0].customer_id, product_id=products[2].product_id, amount=180.00, status="COMPLETED"),
            models.Order(customer_id=customers[1].customer_id, product_id=products[1].product_id, amount=350.00, status="COMPLETED"),
            models.Order(customer_id=customers[2].customer_id, product_id=products[0].product_id, amount=25.00, status="CANCELLED"),
            models.Order(customer_id=customers[3].customer_id, product_id=products[2].product_id, amount=180.00, status="COMPLETED"),
        ]
        db.add_all(orders)

        db.commit()

        print(f"Tenant:          {tenant.id}")
        print(f"Workspace:       {workspace.id}")
        print(f"Semantic model:  {semantic_model.id}")

    finally:
        db.close()


if __name__ == "__main__":
    run()
