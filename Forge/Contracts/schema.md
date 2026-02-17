# ForgeLedger Test — Database Schema

Canonical database schema for this project. The builder contract (S1) requires reading this file before making changes. All migrations must implement this schema. No tables or columns may be added without updating this document first.

---

## Schema Version: 0.1 (initial)

### Conventions

- Table names: snake_case, plural
- Column names: snake_case
- Primary keys: UUID (gen_random_uuid())
- Timestamps: TIMESTAMPTZ for audit fields, DATE for business dates
- Soft delete: No
- Monetary values: DECIMAL(10,2) for currency precision
- All tables include `created_at` timestamp
- ENUM-like constraints implemented via CHECK constraints

---

## Tables

### categories

Stores transaction categories for both income and expense classification.

```sql
CREATE TABLE categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    type            VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Column Notes:**
- `name`: Unique category name across all types (e.g., "Salary", "Groceries", "Freelance")
- `type`: Distinguishes income categories from expense categories
- No `updated_at` as categories are typically created once

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_categories_type ON categories(type);
```

---

### transactions

Stores all financial transactions (both income and expenses) with categorization and metadata.

```sql
CREATE TABLE transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amount          DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    type            VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category_id     UUID REFERENCES categories(id) ON DELETE SET NULL,
    date            DATE NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Column Notes:**
- `amount`: Always stored as positive value; `type` field determines if it's income or expense
- `type`: Must match the type of the referenced category
- `category_id`: Optional categorization; NULL allowed for uncategorized transactions
- `date`: Business date of the transaction (not creation timestamp)
- `description`: Free-text notes about the transaction
- `updated_at`: Tracks when transaction was last modified

**Indexes:**
```sql
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_date ON transactions(date DESC);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_type_date ON transactions(type, date DESC);
```

**Performance Notes:**
- Composite index on `(type, date)` supports filtered date-range queries
- `date DESC` ordering supports most recent transactions first (common query pattern)

---

## Views

### transaction_summary

Provides aggregated view of transactions for dashboard summary.

```sql
CREATE VIEW transaction_summary AS
SELECT
    t.type,
    c.name AS category_name,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    DATE_TRUNC('month', t.date) AS month
FROM transactions t
LEFT JOIN categories c ON t.category_id = c.id
GROUP BY t.type, c.name, DATE_TRUNC('month', t.date);
```

**Purpose:** Pre-aggregates common summary queries for dashboard display without complex application-level aggregation.

---

## Constraints & Business Rules

### Category-Transaction Type Consistency

While not enforced at the database level (to allow flexibility), the application SHOULD ensure that a transaction's `type` matches its category's `type`. This validation is handled in the business logic layer.

**Rationale:** Database-level enforcement would require triggers or complex constraints; application-level validation provides clearer error messages and easier maintenance.

### Amount Validation

- All amounts must be positive (enforced via CHECK constraint)
- Precision: 10 digits total, 2 decimal places (supports up to $99,999,999.99)

### Date Constraints

- Transaction dates should not be in the future (enforced in application layer)
- No lower bound on historical dates (allows import of old records)

---

## Initial Data Seeding

### Default Categories

The following categories should be created during initial database setup:

**Income Categories:**
```sql
INSERT INTO categories (name, type) VALUES
    ('Salary', 'income'),
    ('Freelance', 'income'),
    ('Investment', 'income'),
    ('Other Income', 'income');
```

**Expense Categories:**
```sql
INSERT INTO categories (name, type) VALUES
    ('Groceries', 'expense'),
    ('Rent', 'expense'),
    ('Utilities', 'expense'),
    ('Transportation', 'expense'),
    ('Entertainment', 'expense'),
    ('Healthcare', 'expense'),
    ('Other Expense', 'expense');
```

---

## Schema-to-Phase Traceability

| Table | Phase | Notes |
|-------|-------|-------|
| categories | Phase 0 | Core entity, required for transaction categorization |
| transactions | Phase 0 | Core entity, primary business data |
| transaction_summary | Phase 1 | Optimization view for dashboard performance |

**Phase 0:** Establishes minimal viable schema with both core tables. Categories must exist before transactions due to foreign key relationship.

**Phase 1:** Adds view for improved query performance as data volume grows.

---

## Migration Strategy

### Phase 0 Migration

1. Create `categories` table
2. Create indexes on `categories`
3. Create `transactions` table
4. Create indexes on `transactions`
5. Seed default categories
6. Verify foreign key constraints

### Phase 1 Migration

1. Create `transaction_summary` view
2. Test view performance with sample data

---

## Database Configuration Requirements

### PostgreSQL Version
- Minimum: PostgreSQL 13 (for `gen_random_uuid()` without extension)
- Recommended: PostgreSQL 15+

### Required Extensions
None required for core functionality.

### Connection Pool Settings
- Min connections: 2
- Max connections: 10 (sufficient for single-user or small team usage)
- Idle timeout: 300 seconds

### Neon-Specific Notes
- Database hosted on Neon serverless PostgreSQL
- Automatic connection pooling provided by Neon
- No special configuration required beyond standard PostgreSQL

---

## Backup & Data Integrity

### Backup Strategy
- Daily automated backups via Neon platform
- Point-in-time recovery available (Neon feature)
- No custom backup scripts required

### Data Integrity Checks
- Foreign key constraints ensure referential integrity
- CHECK constraints prevent invalid data entry
- Unique constraints prevent duplicate categories

### Audit Trail
- `created_at` timestamp on all tables provides creation audit
- `updated_at` on transactions tracks modification history
- No explicit audit log table needed for MVP

---

## Performance Considerations

### Expected Data Volume
- Categories: ~20-50 records (low volume, mostly static)
- Transactions: 100-1000 records per user per year (moderate volume)

### Query Patterns
1. **Most Common:** List recent transactions (filtered by type, category, date range)
2. **Dashboard:** Aggregate sums by type and category
3. **Detail View:** Single transaction lookup by ID
4. **Bulk Operations:** Monthly summaries and reports

### Index Strategy
- Primary indexes support CRUD operations
- Composite indexes optimize filtered list queries
- No full-text search indexes needed (simple description text)

### Scaling Notes
- Current schema supports single-user to small team usage (<10 users)
- No partitioning needed at this scale
- No read replicas required
- Neon's serverless architecture handles connection scaling

---

## Future Schema Considerations

### Not Included in MVP (potential Phase 2+)

1. **Multi-user Support**
   - Would require `users` table
   - Foreign key from `transactions` to `users`
   - Row-level security policies

2. **Recurring Transactions**
   - New `recurring_transactions` table
   - Scheduler to generate transactions automatically

3. **Attachments/Receipts**
   - File storage reference table
   - Foreign key from `attachments` to `transactions`

4. **Budget Tracking**
   - `budgets` table with category and amount limits
   - Monthly budget vs. actual comparison

5. **Account/Wallet Support**
   - `accounts` table for multiple bank accounts or wallets
   - Foreign key from `transactions` to `accounts`
   - Balance tracking per account

These features are explicitly OUT OF SCOPE for initial implementation but schema is designed to accommodate future extension without breaking changes.