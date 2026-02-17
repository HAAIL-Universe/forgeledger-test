# ForgeLedger Test — Blueprint (v0.1)

Status: Draft (authoritative for v0.1 build)
Owner: User
Purpose: Define product fundamentals, hard boundaries, and build targets so implementation cannot drift.

---

## 1) Product intent

ForgeLedger Test is a lightweight financial ledger application designed for individuals or small teams who need straightforward transaction tracking without enterprise accounting complexity. Users manually log income and expenses, categorize each transaction, and view their complete financial activity in a unified timeline. The system provides immediate visibility into spending patterns and income sources through a single dashboard view.

The application solves the problem of scattered financial records by providing a centralized, searchable ledger where every dollar in and out is recorded, categorized, and retrievable. Unlike heavyweight accounting software, ForgeLedger Test focuses exclusively on transaction logging and categorization—no invoicing, no payroll, no multi-entity consolidation. It exists because users need a tool that sits between a spreadsheet (too manual, no structure) and QuickBooks (too complex, too expensive).

The primary interaction model is a filterable transaction table with inline add/edit capability. Users see all transactions chronologically by default, filter by type (income/expense), category, or date range, and add new entries via a modal form. Running balance is calculated client-side and displayed per transaction row. Category management is secondary—users can create and edit categories but spend most time in the main transaction view.

---

## Core interaction invariants (must hold)

- Every transaction MUST have exactly one type: income or expense. No mixed or null types.
- Every transaction MUST link to a valid category. Orphaned transactions (category deleted) are prohibited—deletion must cascade or be blocked.
- Transaction amounts MUST be positive decimal values. Negative amounts are represented by type (expense), not sign.
- The transaction list MUST display in reverse chronological order by date (newest first) by default.
- Date filters MUST be inclusive on both start and end dates.
- Category deletion MUST fail if any transactions reference that category (referential integrity enforced at database level).
- Running balance MUST be computed as: sum(income amounts) - sum(expense amounts) up to each transaction's date, displayed in chronological order.

---

## 2) MVP scope (v0.1)

### Must ship

1. **Transaction creation**
   - User submits: amount (decimal, 2 places), type (dropdown: income/expense), category (dropdown from available categories), date (date picker), optional description (textarea, max 500 chars).
   - API validates: amount > 0, type in enum, category exists, date not in future.
   - On success, transaction appears immediately in the list (optimistic UI update).

2. **Transaction list with filters**
   - Main dashboard displays all transactions in a table: date, description, category name, amount, type (color-coded badge: green for income, red for expense).
   - Filter controls above table: type dropdown (all/income/expense), category multi-select, date range picker (start/end).
   - Filters apply instantly without page reload—results update via API call.

3. **Running balance calculation**
   - Each row displays a cumulative balance column: starting from oldest transaction, add income, subtract expense.
   - Balance is computed client-side from filtered transaction set, NOT server-side (keeps API stateless).
   - If filters applied, balance recalculates from filtered subset starting at zero.

4. **Transaction editing**
   - Click any transaction row to open edit modal (same form as creation).
   - All fields editable except transaction ID.
   - PUT request updates transaction; list refreshes to reflect changes.

5. **Transaction deletion**
   - Delete icon per row triggers confirmation dialog ("Delete this transaction? This cannot be undone.").
   - On confirm, DELETE request removes transaction; row disappears from list immediately.

6. **Category management**
   - Secondary page/modal lists all categories: name, type (income/expense).
   - Create category: name (text, max 100 chars, unique), type (dropdown).
   - Edit category: change name only (type immutable after creation to prevent transaction type mismatches).
   - Delete category: fails with error message if any transactions reference it.

7. **Summary statistics**
   - Dashboard header displays: total income (sum of all income transactions), total expenses (sum of all expense transactions), net balance (income - expenses).
   - Statistics update when filters change (reflect filtered set, not all-time totals).

8. **Responsive layout**
   - Application usable on desktop (1280px+), tablet (768-1279px), mobile (320-767px).
   - On mobile: transaction table becomes card list (one transaction per card), filters collapse into drawer.

### Explicitly not MVP (v0.1)

- Multi-user support / user accounts (single-user application, no login)
- Recurring transactions or scheduled entries
- Attachments (receipts, invoices) upload
- Transaction import from CSV or bank feeds
- Budget planning or forecasting
- Multi-currency support (single currency assumed, no exchange rates)
- Audit trail or transaction history (edit/delete logging)
- Search by description text (only category/type/date filters)
- Export to CSV/PDF
- Dashboard charts or graphs (summary statistics only, no visualizations)
- Bulk transaction operations (multi-select delete/edit)
- Tags or labels beyond categories
- Notes or comments on transactions (description field is write-once, edit-via-form)

---

## 3) Hard boundaries (anti-godfile rules)

### API Routes (presentation layer)
- Parse FastAPI request body, call service method, return JSON response.
- MUST NOT contain business logic, SQL queries, or data validation beyond schema enforcement.
- MUST NOT compute running balances, filter logic, or summary statistics.
- MUST NOT import SQLAlchemy models or Pydantic schemas from repository layer.

### Services (business logic layer)
- Validate business rules: amount > 0, type enum, category existence, date validity.
- Orchestrate repository calls for CRUD operations.
- Compute summary statistics (total income, expenses, net) from transaction lists.
- MUST NOT contain FastAPI decorators, SQL query text, or HTTP response construction.
- MUST NOT import database connection objects or session management.

### Repositories (data access layer)
- Execute all database reads and writes via SQLAlchemy ORM.
- Return domain objects (dataclasses or Pydantic models), NOT ORM models directly.
- MUST NOT contain business logic, validation rules, or summary calculations.
- MUST NOT import FastAPI dependencies or service layer code.

### Frontend Components (UI layer)
- Render UI, handle user input events, call API client methods.
- Compute client-side running balance from transaction array.
- MUST NOT contain API fetch logic (use dedicated API client module).
- MUST NOT contain business validation rules (rely on server responses).

### Frontend API Client (data fetching layer)
- Wrap all HTTP calls to backend in typed functions.
- Handle request serialization, response deserialization, error parsing.
- MUST NOT contain React hooks, component state, or UI rendering logic.
- MUST NOT perform client-side validation or data transformation beyond JSON mapping.

### Database Migration Scripts
- Define schema changes in Alembic migrations.
- MUST NOT contain data transformations, business logic, or API calls.
- Each migration must be reversible (downgrade implemented).

---

## 4) Deployment target

- **Backend**: Render web service (Python FastAPI app via uvicorn), single process, no worker queue.
- **Frontend**: Render static site (Vite build output served via CDN).
- **Database**: Neon PostgreSQL (managed, serverless).
- **Expected load**: Under 1,000 transactions total, single user, no concurrent write contention.
- **Scaling assumptions**: No horizontal scaling needed in MVP. Database connection pool size = 5. API response time target: <200ms for transaction list (100 rows), <50ms for single transaction CRUD.
- **Data retention**: No automatic deletion or archival. User manually deletes transactions.
- **Backup strategy**: Rely on Neon's automated backups (no custom backup implementation in MVP).

---

## 5) Data integrity constraints (enforced at database level)

- `transactions.amount`: DECIMAL(10,2), CHECK (amount > 0), NOT NULL
- `transactions.type`: VARCHAR(10), CHECK (type IN ('income', 'expense')), NOT NULL
- `transactions.date`: DATE, NOT NULL, no future dates enforced at application layer (not DB constraint)
- `transactions.category_id`: UUID, FOREIGN KEY REFERENCES categories(id) ON DELETE RESTRICT
- `categories.name`: VARCHAR(100), NOT NULL, UNIQUE
- `categories.type`: VARCHAR(10), CHECK (type IN ('income', 'expense')), NOT NULL
- All primary keys: UUID v4, generated by database or application before insert
- `transactions.created_at`: TIMESTAMP, DEFAULT NOW(), immutable after insert

---

## 6) API contract (REST endpoints)

### POST /transactions
- Request body: `{ "amount": number, "type": "income" | "expense", "category_id": string (UUID), "date": string (ISO 8601 date), "description": string | null }`
- Response 201: `{ "id": string, "amount": number, "type": string, "category_id": string, "date": string, "description": string | null, "created_at": string (ISO 8601 timestamp) }`
- Response 400: `{ "error": string }` (validation failure: amount <= 0, invalid type, category not found, date in future)
- Response 422: Schema validation error (missing required fields)

### GET /transactions
- Query params: `type` (optional: "income" | "expense"), `category_id` (optional: UUID), `start_date` (optional: ISO 8601 date), `end_date` (optional: ISO 8601 date)
- Response 200: `{ "transactions": [ { ... transaction object ... } ] }` (array of transactions matching filters, ordered by date DESC)
- Response 400: Invalid query param values (malformed UUID, invalid date format)

### GET /transactions/:id
- Response 200: `{ ... transaction object ... }`
- Response 404: `{ "error": "Transaction not found" }`

### PUT /transactions/:id
- Request body: same as POST (all fields required, even if unchanged)
- Response 200: `{ ... updated transaction object ... }`
- Response 400: Validation error
- Response 404: Transaction not found

### DELETE /transactions/:id
- Response 204: No content (success)
- Response 404: Transaction not found

### POST /categories
- Request body: `{ "name": string (max 100 chars), "type": "income" | "expense" }`
- Response 201: `{ "id": string, "name": string, "type": string }`
- Response 400: Validation error (duplicate name, invalid type)

### GET /categories
- Query params: `type` (optional: "income" | "expense")
- Response 200: `{ "categories": [ { "id": string, "name": string, "type": string } ] }`

### PUT /categories/:id
- Request body: `{ "name": string }` (type immutable)
- Response 200: `{ ... updated category object ... }`
- Response 400: Validation error (duplicate name)
- Response 404: Category not found

### DELETE /categories/:id
- Response 204: No content (success)
- Response 400: `{ "error": "Cannot delete category with existing transactions" }` (referential integrity violation)
- Response 404: Category not found

---

## 7) Frontend state management rules

- **Global state**: Transaction list, category list, active filters (type, category, date range).
- **Local component state**: Form inputs, modal open/closed, loading indicators.
- **State update flow**: User action → API client call → update global state → React re-render.
- **Optimistic updates**: Transaction creation and deletion apply optimistically (update UI immediately, rollback on API error).
- **Filter persistence**: Filters reset on page reload (no URL state or localStorage in MVP).
- **Running balance computation**: Recalculated on every render from current transaction list (no memoization in MVP—list small enough for brute-force recalc).

---

## 8) Error handling standards

### Backend (FastAPI)
- 400: Client error (validation failure, business rule violation). Return JSON: `{ "error": "descriptive message" }`.
- 404: Resource not found. Return JSON: `{ "error": "Transaction not found" }` or similar.
- 422: Pydantic schema validation error (missing fields, type mismatches). FastAPI default response.
- 500: Unhandled exception. Log stack trace, return JSON: `{ "error": "Internal server error" }` (no details exposed to client).

### Frontend (React)
- API call failure: Display toast notification with error message from API response.
- Network error (no response): Display toast: "Network error. Please try again."
- Validation error (400): Highlight form fields with error messages from API.
- Optimistic update rollback: Revert UI change, display toast with error message.

---

## 9) Database indexing requirements

- `transactions.date`: Index (DESC) for fast chronological queries.
- `transactions.category_id`: Index for filter queries.
- `transactions.type`: Index for filter queries.
- `categories.name`: Unique constraint (implicitly indexed).
- Composite index on `(type, date)` for common filter combination.

---

## 10) Build and test targets (MVP)

### Backend tests (pytest)
- Repository layer: Unit tests for all CRUD operations (mock database).
- Service layer: Unit tests for validation logic, summary calculations (mock repository).
- API routes: Integration tests hitting real test database (Neon dev instance or local Postgres in Docker).
- Coverage target: 80% line coverage for services and repositories.

### Frontend tests (Vitest)
- Component rendering tests: Verify transaction list, form, filters render without crashing.
- API client tests: Mock fetch calls, verify request/response handling.
- Running balance calculation: Unit test balance logic with sample transaction arrays.
- Coverage target: 60% line coverage (lower bar for UI in MVP).

### Manual QA checklist (before v0.1 release)
- Create income and expense transactions across multiple categories.
- Edit transaction: change amount, category, date, description.
- Delete transaction: verify it disappears from list and summary updates.
- Apply filters: type, category, date range (individually and combined).
- Create, edit, delete categories.
- Attempt to delete category with transactions (verify error message).
- Test responsive layout on mobile (DevTools).
- Verify running balance recalculates correctly after filtering.

---

## 11) Non-functional requirements

### Performance
- Transaction list load (100 rows): <200ms (backend query + serialization).
- Transaction creation: <100ms (single INSERT).
- Category list load: <50ms (typically <20 categories).
- Frontend initial page load: <1s (Vite production build, gzipped).

### Security
- No authentication in MVP (acknowledged risk—single-user assumption).
- SQL injection protection: Use parameterized queries via SQLAlchemy ORM (never string interpolation).
- CORS: Backend allows frontend origin only (hardcoded in FastAPI middleware).
- Input sanitization: Pydantic schemas enforce types, max lengths.

### Reliability
- Database connection retry: 3 attempts with exponential backoff on connection failure.
- Transaction atomicity: Each API call wraps database operations in a transaction (commit on success, rollback on error).
- Idempotency: PUT and DELETE are idempotent (repeated calls produce same result).

### Observability
- Backend logging: INFO level for all API requests (method, path, response status, duration). ERROR level for exceptions.
- Log destination: stdout (captured by Render).
- No structured logging or tracing in MVP (plaintext logs sufficient for single-user debugging).

---

End of blueprint. This document is the authoritative source for ForgeLedger Test v0.1 implementation. Any deviation requires explicit blueprint amendment.