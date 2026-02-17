# ForgeLedger Test — Manifesto (v0.1)

This document defines the non-negotiable principles for building ForgeLedger Test.
If implementation conflicts with this manifesto, implementation is wrong.

---

## 1) Product principle: transaction-centric, chronological truth

ForgeLedger Test is a ledger-first application where transactions are the atomic unit of financial truth.

- Every financial event is represented as a transaction record with an immutable creation timestamp.
- The dashboard displays transactions in chronological order by transaction date, not entry date.
- Running balances are calculated from the complete transaction history, never stored as cached values.
- Transaction history is append-preferred: updates are allowed but discouraged through UI friction (confirmation dialogs).
- If a transaction exists in the database, it must be visible in the UI. No hidden or soft-deleted records in MVP.

---

## 2) Type-first, schema-first, constraint-enforced

ForgeLedger Test is built on strict type contracts at every layer.

- Database schema is the canonical source of truth for data structure.
- Transaction type (`income` | `expense`) is enforced at database level via CHECK constraint, never trusted from application logic alone.
- Category relationships are enforced via foreign keys — orphaned transactions are impossible by design.
- Backend Pydantic models mirror database schema exactly, including constraints (e.g., DECIMAL(10,2) precision, type enums).
- Frontend TypeScript types are derived from API contracts, not invented independently.
- If a field is NOT NULL in the database, it must be required in forms and API validation.

---

## 3) No godfiles, no blurred boundaries

Every layer has a single, explicit responsibility.

### Backend (Python)
- **Routes** — HTTP request parsing, response serialization, status codes only. No business logic.
- **Services** — Business logic orchestration: validation, transaction creation, balance calculation, category management.
- **Repositories** — Database queries only. Returns domain objects, not raw SQL results.
- **Models** — Pydantic schemas for API contracts and database entities. No methods, pure data structures.

### Frontend (React + TypeScript)
- **Components** — UI rendering and user interaction only. No API calls, no business logic.
- **API Services** — HTTP client functions for backend communication. Returns typed responses.
- **Hooks** — State management and side effects (data fetching, form state).
- **Types** — TypeScript interfaces mirroring API contracts.

### Violations that are bugs
- A route that queries the database directly.
- A component that calls `fetch()` instead of using an API service.
- A repository that contains validation logic.
- A service that formats API responses (that's the route's job).

---

## 4) Explicit over implicit, boring over clever

ForgeLedger Test prioritizes readability and debuggability over abstraction.

- Category filtering is done via SQL WHERE clauses, not in-memory array filters.
- Date range queries use explicit `date >= start_date AND date <= end_date`, not date math libraries unless necessary.
- Transaction amounts are stored as DECIMAL(10,2) and handled as strings in JSON, never as floating-point numbers.
- API error responses include explicit error codes and human-readable messages, not just HTTP status codes.
- No magic: a developer should be able to trace a transaction creation from form submission → API call → service method → repository insert → database row.

---

## 5) Confirm-before-delete, warn-before-update

ForgeLedger Test respects the permanence of financial records.

### Actions requiring confirmation
- **Transaction deletion** — "Are you sure you want to delete this transaction? This action cannot be undone."
- **Category deletion** — "This category is used by X transactions. Are you sure you want to delete it?" (Blocked if foreign key constraint would fail.)
- **Transaction update** — No confirmation required but shows "Last modified" timestamp in UI after save.

### Actions exempt from confirmation
- **Transaction creation** — Direct submission, no confirmation dialog.
- **Category creation** — Direct submission.
- **Filtering/viewing data** — Read-only operations never require confirmation.

### Constraint violations
- Attempting to delete a category used by transactions returns a 400 error with clear message: "Cannot delete category '{name}' — it is used by {count} transactions."
- Attempting to create a transaction with invalid type returns 400: "Transaction type must be 'income' or 'expense'."

---

## 6) Financial integrity: precision and audit trail

ForgeLedger Test treats financial data with accounting-level rigor.

- Transaction amounts are stored as DECIMAL(10,2), never FLOAT or INTEGER cents.
- Currency precision is always two decimal places in storage, API, and UI.
- The `created_at` timestamp is system-generated and immutable — it records when the transaction was entered.
- The `date` field is user-provided and represents when the transaction occurred — this is used for chronological display.
- Running balance calculations are deterministic: same transaction set → same balance every time.
- If a transaction is updated, the `created_at` timestamp does not change (update timestamp would be a separate field in a future version).

### Audit requirements
- Every transaction stores: amount, type, date, description, category, creation timestamp.
- API responses for transaction lists include all fields, not summary views.
- Deletes are hard deletes in MVP (soft deletes and audit logs are post-MVP).

---

## 7) Data locality and privacy by default

ForgeLedger Test operates as a single-tenant system with no authentication in MVP.

- No user accounts, no multi-tenancy — all transactions belong to the single application instance.
- Database hosted on Neon PostgreSQL with connection string stored in environment variables, never committed to version control.
- No third-party analytics or tracking in MVP.
- No external API calls except to the application's own backend.
- Transaction data is never exported automatically — user must explicitly request data export (post-MVP feature).

### Environment isolation
- Local development uses `.env.local` with localhost database connection.
- Production deployment (future) uses `.env.production` with Neon credentials.
- No shared database between environments — local dev uses separate database instance.

---

## 8) REST-first, simple endpoints, predictable behavior

ForgeLedger Test uses RESTful conventions without over-engineering.

- Resource endpoints follow standard patterns: `GET /transactions`, `POST /transactions`, `GET /transactions/:id`, etc.
- List endpoints support query parameters for filtering: `?type=income`, `?category_id=uuid`, `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`.
- Successful creates return `201 Created` with the created resource in response body.
- Successful updates return `200 OK` with the updated resource.
- Successful deletes return `204 No Content` with empty body.
- Not found returns `404` with `{"error": "Transaction not found"}`.
- Validation failures return `400` with detailed error messages.

### No surprises
- `GET` requests never mutate data.
- `DELETE` requests are idempotent — deleting an already-deleted resource returns 404, not 500.
- Filtering returns empty arrays if no matches, not null or errors.