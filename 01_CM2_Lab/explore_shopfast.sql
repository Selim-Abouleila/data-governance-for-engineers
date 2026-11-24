-- CM 2 Lab — Part 2: Explore the 7 ShopFast datasets in PostgreSQL (schema: raw)
-- Connect to localhost:5432, db: shopfast, user: shopfast_admin, password: shopfast_admin

-- 1. Row counts for all 7 datasets
SELECT 'customers' AS dataset, COUNT(*) AS row_count FROM raw.customers
UNION ALL SELECT 'products', COUNT(*) FROM raw.products
UNION ALL SELECT 'orders', COUNT(*) FROM raw.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM raw.order_items
UNION ALL SELECT 'payments', COUNT(*) FROM raw.payments
UNION ALL SELECT 'support_tickets', COUNT(*) FROM raw.support_tickets
UNION ALL SELECT 'marketing_campaign_export', COUNT(*) FROM raw.marketing_campaign_export;

-- 2. customers: missing values, duplicate IDs, country spellings, loyalty_tier spellings
SELECT
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE email IS NULL) AS missing_email,
  COUNT(*) FILTER (WHERE phone IS NULL) AS missing_phone,
  COUNT(*) FILTER (WHERE country IS NULL) AS missing_country,
  COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_customer_ids
FROM raw.customers;

SELECT country, COUNT(*) FROM raw.customers GROUP BY country ORDER BY COUNT(*) DESC;
SELECT loyalty_tier, COUNT(*) FROM raw.customers GROUP BY loyalty_tier ORDER BY COUNT(*) DESC;

-- 3. products: missing/negative prices, duplicate SKUs, dirty category names
SELECT * FROM raw.products WHERE unit_price_eur IS NULL OR unit_price_eur::NUMERIC <= 0;
SELECT sku, COUNT(*) FROM raw.products GROUP BY sku HAVING COUNT(*) > 1;
SELECT category, COUNT(*) FROM raw.products GROUP BY category ORDER BY category;

-- 4. orders: duplicate order_ids, missing/future dates, negative totals, orphan customers, status variants
SELECT order_id, COUNT(*) FROM raw.orders GROUP BY order_id HAVING COUNT(*) > 1;
SELECT * FROM raw.orders WHERE order_date IS NULL OR order_date > '2026-11-24' OR total_amount_eur::NUMERIC <= 0;
SELECT status, COUNT(*) FROM raw.orders GROUP BY status ORDER BY COUNT(*) DESC;
SELECT COUNT(*) AS orphan_orders
FROM raw.orders o
LEFT JOIN raw.customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 5. order_items: non-positive quantities and orphan product_ids
SELECT * FROM raw.order_items WHERE quantity::INT <= 0;
SELECT oi.*
FROM raw.order_items oi
LEFT JOIN raw.products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- 6. payments: card_last4 populated on non-card methods or missing on card payments
SELECT method,
       COUNT(*) AS total,
       COUNT(card_last4) AS with_card_last4,
       COUNT(*) - COUNT(card_last4) AS without_card_last4
FROM raw.payments
GROUP BY method;

-- 7. support_tickets: unstructured PII (IBANs, phones, emails, birth dates) in message and agent_notes
SELECT ticket_id, customer_id, message, agent_notes
FROM raw.support_tickets
WHERE message ~* '(FR[0-9]{2}|@|[0-9]{2}[ .-][0-9]{2}[ .-][0-9]{2})'
   OR agent_notes ~* 'born [0-9]{4}-[0-9]{2}-[0-9]{2}'
LIMIT 20;

-- 8. marketing_campaign_export: email drift / erased emails still present in marketing export
SELECT m.customer_id, m.email AS export_email, c.email AS master_email,
       m.loyalty_tier AS export_tier, c.loyalty_tier AS master_tier
FROM raw.marketing_campaign_export m
LEFT JOIN raw.customers c ON m.customer_id = c.customer_id
WHERE m.email IS DISTINCT FROM c.email
   OR m.loyalty_tier IS DISTINCT FROM c.loyalty_tier;
