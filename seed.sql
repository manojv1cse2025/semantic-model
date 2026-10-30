-- ===== The "dictionary" (semantic model) =====

INSERT INTO tenants (id, name) VALUES
('11111111-1111-1111-1111-111111111111', 'Demo Tenant');

INSERT INTO workspaces (id, tenant_id, name) VALUES
('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Demo Workspace');

INSERT INTO semantic_models (id, workspace_id, name, description, status) VALUES
('33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222',
 'Ecommerce Model', 'Demo semantic model for orders/customers/products', 'active');

-- Entities: which business objects map to which physical tables
INSERT INTO entities (id, semantic_model_id, name, physical_table, primary_key) VALUES
('44444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', 'Customer', 'customers', 'customer_id'),
('55555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', 'Order', 'orders', 'order_id'),
('66666666-6666-6666-6666-666666666666', '33333333-3333-3333-3333-333333333333', 'Product', 'products', 'product_id');

-- Dimensions: things you can group/filter by
INSERT INTO dimensions (id, semantic_model_id, entity_id, name, physical_column, data_type, synonyms) VALUES
('77777777-7777-7777-7777-777777777771', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444',
 'country', 'customers.country', 'text', ARRAY['country', 'geography', 'customer country']),
('77777777-7777-7777-7777-777777777772', '33333333-3333-3333-3333-333333333333', '66666666-6666-6666-6666-666666666666',
 'category', 'products.category', 'text', ARRAY['category', 'product category', 'product type']);

-- Metrics: the one true definition for each measurable thing
INSERT INTO metrics (id, semantic_model_id, name, expression, aggregation, synonyms) VALUES
('88888888-8888-8888-8888-888888888881', '33333333-3333-3333-3333-333333333333',
 'revenue', 'SUM(orders.amount)', 'sum', ARRAY['sales', 'income', 'total sales', 'revenue']),
('88888888-8888-8888-8888-888888888882', '33333333-3333-3333-3333-333333333333',
 'order_count', 'COUNT(DISTINCT orders.order_id)', 'count', ARRAY['orders', 'number of orders', 'order volume']);

-- Relationships: how tables legally join together
INSERT INTO relationships (id, semantic_model_id, from_entity_id, to_entity_id, relationship_type, join_sql) VALUES
('99999999-9999-9999-9999-999999999991', '33333333-3333-3333-3333-333333333333',
 '55555555-5555-5555-5555-555555555555', '44444444-4444-4444-4444-444444444444',
 'many_to_one', 'orders.customer_id = customers.customer_id'),
('99999999-9999-9999-9999-999999999992', '33333333-3333-3333-3333-333333333333',
 '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666',
 'many_to_one', 'orders.product_id = products.product_id');

-- Business rules: the fine print, applied automatically
INSERT INTO business_rules (id, semantic_model_id, name, rule) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', '33333333-3333-3333-3333-333333333333',
 'valid_revenue', 'orders.status NOT IN (''CANCELLED'', ''REFUNDED'')'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', '33333333-3333-3333-3333-333333333333',
 'active_customer', 'customers.status = ''ACTIVE''');

-- ===== The actual business data =====

INSERT INTO customers (name, country, status) VALUES
('Aarav Sharma', 'India', 'ACTIVE'),
('Priya Nair', 'India', 'ACTIVE'),
('John Smith', 'USA', 'ACTIVE'),
('Emily Clark', 'USA', 'ACTIVE'),
('Hans Müller', 'Germany', 'ACTIVE'),
('Sophie Dubois', 'France', 'ACTIVE'),
('Liam O''Brien', 'UK', 'ACTIVE'),
('Wei Chen', 'China', 'INACTIVE'),
('Ravi Kumar', 'India', 'ACTIVE'),
('Anna Kowalski', 'Poland', 'ACTIVE');

INSERT INTO products (name, category, price) VALUES
('Wireless Mouse', 'Electronics', 799.00),
('Bluetooth Speaker', 'Electronics', 2499.00),
('Yoga Mat', 'Fitness', 999.00),
('Running Shoes', 'Fitness', 3499.00),
('Coffee Maker', 'Home', 4499.00),
('Desk Lamp', 'Home', 1299.00),
('Notebook Set', 'Stationery', 299.00),
('Backpack', 'Accessories', 1999.00);

INSERT INTO orders (customer_id, product_id, amount, status, order_date) VALUES
(1, 1, 799.00, 'COMPLETED', '2026-03-05'),
(1, 3, 999.00, 'COMPLETED', '2026-04-12'),
(2, 5, 4499.00, 'COMPLETED', '2026-04-20'),
(2, 2, 2499.00, 'CANCELLED', '2026-05-01'),
(3, 4, 3499.00, 'COMPLETED', '2026-05-10'),
(3, 7, 299.00, 'COMPLETED', '2026-06-02'),
(4, 6, 1299.00, 'COMPLETED', '2026-06-15'),
(5, 8, 1999.00, 'COMPLETED', '2026-07-01'),
(5, 1, 799.00, 'REFUNDED', '2026-07-18'),
(6, 2, 2499.00, 'COMPLETED', '2026-07-25'),
(7, 3, 999.00, 'COMPLETED', '2026-08-03'),
(9, 4, 3499.00, 'COMPLETED', '2026-08-14'),
(9, 5, 4499.00, 'COMPLETED', '2026-08-30'),
(10, 6, 1299.00, 'COMPLETED', '2026-09-02'),
(1, 8, 1999.00, 'COMPLETED', '2026-09-05');


INSERT INTO dimensions (id, semantic_model_id, entity_id, name, physical_column, data_type, synonyms) VALUES
('77777777-7777-7777-7777-777777777773', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555',
 'order_date', 'orders.order_date', 'date', ARRAY['order date', 'date', 'month', 'last month']);