# ForgeLedger Test — Manifesto (v0.1)

This document defines the non-negotiable principles for building ForgeLedger Test.
If implementation conflicts with this manifesto, implementation is wrong.

---

## 1) Product principle: ledger-first, transaction-accurate

ForgeLedger Test is a financial ledger that presents a unified, chronological view of all monetary activity.

- The transaction list is the primary interface — not summary boxes, not charts.
- Every transaction is either income or expense. No ambiguous states, no "pending" or "draft" transactions.
- The running balance is always derivable from the transaction log. Balance is computed, never stored separately.
- Date and amount are immutable facts. If a transaction was entered incorrectly, it's edited transparently — not silently corrected.
- Missing or incomplete transactions are visible as problems, not hidden.

---

## 2) Schema-first, data integrity enforced

ForgeLedger Test's data model is its contract with reality.

- The PostgreSQL schema (`transactions`, `categories`) is the source of truth.
- Database constraints (`CHECK`, `NOT NULL`, `FOREIGN KEY`) enforce business rules at the data layer.
- Transaction `type` must be `'income'` or `'expense'` — enforced by CHECK constraint, not application logic.
- Category assignments are referential. A transaction cannot reference a category that doesn't exist.
- If the database rejects a write, the application reports the failure honestly — no silent fallbacks.

---

## 3) No godfiles, clean boundaries

Every layer has a defined role. Mixing responsibilities is a defect.

### Backend layers (Python)
- **Routes** — HTTP request parsing, response serialization, status codes. No database calls, no calculations.
- **Services** — Business logic: transaction validation, balance calculation, category usage checks. Orchestrates repository calls.
- **Repositories** — SQL queries only. No validation, no business rules, no formatting.

### Frontend layers (TypeScript/React)
- **Components** — UI rendering and user interaction. No direct API calls.
- **API clients** — HTTP requests to backend. No state management, no UI logic.
- **State management** — Application state (transaction list, filters, selected category). No data fetching logic.

Violations of these boundaries are bugs, even if the feature appears to work.

---

## 4) Manual entry over automation

ForgeLedger Test is built for deliberate, user-driven financial tracking.

- Every transaction is manually entered by the user. No CSV imports, no bank API integrations, no auto-categorization in MVP.
- Users explicitly choose the category, date, amount, and type for each transaction.
- The system provides structure (categories, transaction types) but never assumes intent.
- Filters are assistive tools for viewing transactions, not automated rules.

---

## 5) Transparency over convenience

The system prioritizes clarity and auditability over speed or "smart" features.

- Deleting a transaction requires explicit confirmation. No undo stack — deletions are permanent.
- Editing a transaction shows what changed. The `updated_at` timestamp (if implemented) reflects modification.
- Category deletion is blocked if transactions reference it. User must reassign transactions before deletion.
- Filter state is explicit. The URL or UI clearly shows active filters (date range, category, type).
- Error messages state the problem directly: "Category 'Rent' cannot be deleted because 12 transactions reference it."

---

## 6) Decimal precision for money

Financial amounts are precise, not approximate.

- All monetary amounts are stored as `DECIMAL(10,2)` — never `FLOAT`, never `INTEGER` cents.
- Currency display rounds to two decimal places in the UI but preserves exact values in the database.
- Balance calculations use decimal arithmetic. A running balance of $1000.00 minus $500.50 equals $499.50, exactly.
- Totals and summaries are computed from transaction data, not cached or estimated.

---

## 7) Confirm-before-write (destructive actions only)

ForgeLedger Test requires confirmation for actions that lose data.

### Requires confirmation
- Deleting a transaction
- Deleting a category (if allowed by referential integrity)
- Bulk actions (if implemented: "delete all filtered transactions")

### No confirmation required
- Creating a transaction (user is actively filling a form)
- Editing a transaction (changes are explicit in the form)
- Applying filters (read-only operation)
- Creating a category (non-destructive)

Confirmation dialogs state what will be lost:
- "Delete transaction '$250.00 - Groceries' from 2024-12-15? This cannot be undone."

---

## 8) Privacy by default (future-proofing)

ForgeLedger Test's MVP has no authentication, but privacy principles are embedded.

- Financial data (transactions, categories) is stored only in the user's PostgreSQL instance.
- No third-party analytics, tracking, or telemetry in MVP.
- Database credentials are environment variables, never hardcoded.
- If multi-user support is added later: transactions are scoped to user. No cross-user visibility, no shared categories by default.
- If authentication is added: passwords are hashed (bcrypt/argon2), never stored plaintext.