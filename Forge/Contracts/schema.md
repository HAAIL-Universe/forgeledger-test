# ForgeLedger Test — Database Schema

Canonical database schema for this project. The builder contract (S1) requires reading this file before making changes. All migrations must implement this schema. No tables or columns may be added without updating this document first.

---

## Schema Version: 0.1 (initial)

### Conventions

- Table names: snake_case, plural
- Column names: snake_case
- Primary keys: UUID (gen_random_uuid())
- Timestamps: TIMESTAMPTZ for audit columns, DATE for transaction dates
- Decimal precision: DECIMAL(10,2) for monetary amounts
- Soft delete: No
- CHECK constraints: Used for enum-like columns (type fields)
- All tables include created_at timestamps for audit purposes
- Foreign keys use ON DELETE CASCADE where appropriate to maintain referential integrity

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

**Column Details:**
- `id`: Unique identifier for the category
- `name`: Display name of the category (must be unique across all categories)
- `type`: Category classification, either 'income' or 'expense'
- `created_at`: Timestamp when category was created

**Constraints:**
- UNIQUE on `name` ensures no duplicate category names
- CHECK constraint on `type` enforces only valid values

```sql
CREATE UNIQUE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_categories_type ON categories(type);
```

---

### transactions

Stores all financial transactions (both income and expenses) in a unified ledger.

```sql
CREATE TABLE transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amount          DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    type            VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category_id     UUID REFERENCES categories(id) ON DELETE RESTRICT,
    date            DATE NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Column Details:**
- `id`: Unique identifier for the transaction
- `amount`: Transaction amount in decimal format (10 digits total, 2 decimal places)
- `type`: Transaction type, either 'income' or 'expense'
- `category_id`: Foreign key reference to categories table (nullable to allow uncategorized transactions)
- `date`: The date when the transaction occurred (not the entry date)
- `description`: Optional text description providing transaction details
- `created_at`: Timestamp when transaction record was created
- `updated_at`: Timestamp when transaction record was last modified

**Constraints:**
- CHECK constraint on `amount` ensures only positive values
- CHECK constraint on `type` enforces only valid values
- FOREIGN KEY on `category_id` with RESTRICT to prevent deletion of categories with associated transactions
- NOT NULL on `amount`, `type`, and `date` as these are required fields

```sql
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_date ON transactions(date DESC);
CREATE INDEX idx_transactions_date_type ON transactions(date DESC, type);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
```

**Index Rationale:**
- `idx_transactions_category_id`: Supports filtering by category
- `idx_transactions_type`: Supports filtering by transaction type
- `idx_transactions_date`: Supports date-based sorting and filtering (DESC for recent-first views)
- `idx_transactions_date_type`: Composite index for combined date and type filtering
- `idx_transactions_created_at`: Supports audit queries and chronological views

---

## Schema-to-Phase Traceability Matrix

| Table | Phase | Rationale |
|-------|-------|-----------|
| categories | Phase 0 (Foundation) | Core reference data required before any transactions can be created |
| transactions | Phase 0 (Foundation) | Primary business entity, central to all application functionality |

---

## Data Integrity Rules

### Foreign Key Policies

1. **categories → transactions**
   - Policy: ON DELETE RESTRICT
   - Rationale: Categories with associated transactions cannot be deleted to maintain data integrity and prevent orphaned transaction records
   - Application logic must handle category deletion by either reassigning transactions or preventing deletion

### CHECK Constraints

1. **Transaction Amount**
   - Constraint: `amount > 0`
   - Rationale: Negative amounts are semantically incorrect; transaction type ('income' vs 'expense') indicates the direction of cash flow

2. **Transaction Type**
   - Constraint: `type IN ('income', 'expense')`
   - Rationale: Enforces valid transaction classifications at database level

3. **Category Type**
   - Constraint: `type IN ('income', 'expense')`
   - Rationale: Enforces valid category classifications at database level

---

## Seed Data Requirements

### Default Categories

The application should include default categories for common transaction types:

**Income Categories:**
- Salary
- Freelance
- Investment
- Other Income

**Expense Categories:**
- Housing
- Transportation
- Food & Dining
- Utilities
- Healthcare
- Entertainment
- Shopping
- Other Expense

These should be created during initial database setup or first application launch.

---

## Migration Strategy

1. **Phase 0 Initial Migration:**
   - Create categories table
   - Create transactions table
   - Create all indexes
   - Insert seed data for default categories

2. **Future Migrations:**
   - All schema changes must be backwards-compatible where possible
   - Breaking changes require version increment in this document
   - Migrations must be idempotent and reversible

---

## Query Performance Considerations

1. **Common Query Patterns:**
   - List recent transactions (ORDER BY date DESC)
   - Filter by date range (WHERE date BETWEEN)
   - Filter by category (WHERE category_id =)
   - Filter by type (WHERE type =)
   - Combined filters (date + type + category)

2. **Index Coverage:**
   - All common filter and sort operations are covered by indexes
   - Composite index on (date, type) optimizes most common filtered views

3. **Expected Data Volume:**
   - Moderate transaction volume (hundreds to thousands of records)
   - Low category volume (typically 10-50 categories)
   - Indexes sufficient for expected scale

---

## Notes

- No authentication/user system required for MVP
- No soft delete; transactions can be permanently deleted
- No audit trail beyond created_at/updated_at timestamps
- Future consideration: Add user_id column if multi-user support is needed
- Future consideration: Add recurring transaction support
- Future consideration: Add attachment/receipt storage references