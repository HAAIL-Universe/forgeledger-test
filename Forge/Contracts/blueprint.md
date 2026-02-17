# ForgeLedger Test — Blueprint (v0.1)

Status: Draft (authoritative for v0.1 build)
Owner: User
Purpose: Define product fundamentals, hard boundaries, and build targets so implementation cannot drift.

---

## 1) Product intent

ForgeLedger Test is a lightweight financial ledger application that provides individuals and small teams with a unified view of their income and expenses. It solves the problem of fragmented financial tracking by consolidating all transactions—both incoming and outgoing—into a single, chronological record with categorical organization.

Users manually log transactions as they occur, assigning each entry to a predefined or custom category (e.g., "Salary," "Groceries," "Utilities"). The system maintains a running ledger that shows the financial activity over time, enabling users to understand cash flow patterns without the complexity of full accounting software. Unlike spreadsheets, ForgeLedger provides structured data validation, category management, and filtered views that make financial review quick and reliable.

The primary interaction model is a dashboard-centric web interface: users see a comprehensive transaction list with filtering capabilities (by type, category, date range), a summary view showing totals and balances, and inline forms for creating or editing entries. The system prioritizes data integrity through database constraints and maintains a clear audit trail via timestamp tracking on all transactions.

---

## Core interaction invariants (must hold)

- Every transaction MUST have a valid type (income or expense), an amount, and a date. No transaction can exist without these three fields.
- Every transaction with a category_id MUST reference an existing category in the database. Orphaned transactions are not allowed.
- Every category MUST have a unique name within the system. Two categories cannot share the same name.
- Deleting a category MUST fail if transactions reference it. Users must first reassign or delete dependent transactions.
- The transaction list MUST display entries in reverse chronological order (newest first) by default.
- All monetary amounts MUST be stored with exactly two decimal places. No fractional cents.
- Transaction type and category type MUST be validated at the database level. Invalid values cannot be persisted.

---

## 2) MVP scope (v0.1)

### Must ship

1. **Transaction creation**
   - User fills a form with amount (decimal, required), type (income/expense dropdown, required), category (dropdown of existing categories, optional), date (date picker, required), and description (text area, optional).
   - On submit, transaction is persisted to PostgreSQL with a generated UUID and created_at timestamp.
   - Form validates: amount > 0, type is either 'income' or 'expense', date is valid, category exists if provided.

2. **Transaction list view**
   - Dashboard displays all transactions in a table with columns: date, type, amount, category name, description (truncated), and actions (edit/delete).
   - Transactions are sorted by date descending (most recent first).
   - Each row shows type as a colored badge (green for income, red for expense).
   - Amount displays with currency symbol ($) and two decimal places.

3. **Transaction filtering**
   - Filter panel above transaction table with three controls: type dropdown (all/income/expense), category multi-select, date range picker (start and end dates).
   - Filters apply immediately on change, updating the transaction list via API call.
   - Filters combine with AND logic: a transaction must match all active filters to appear.

4. **Transaction update**
   - Click edit icon on a transaction row to open the same form used for creation, pre-populated with existing values.
   - User can modify any field. On save, PUT request updates the transaction.
   - Updated transaction reflects changes immediately in the list view.

5. **Transaction deletion**
   - Click delete icon to trigger confirmation dialog ("Delete this transaction? This cannot be undone.").
   - On confirm, DELETE request removes the transaction from the database.
   - Transaction disappears from list view immediately.

6. **Category management**
   - Separate page/modal accessible from main navigation showing all categories in a list.
   - Each category displays: name, type (income/expense), and action buttons (edit/delete).
   - User can create a new category via form: name (text input, required, unique), type (income/expense dropdown, required).
   - User can edit category name or type. On save, PUT request updates the category.
   - Attempting to delete a category with dependent transactions shows error message: "Cannot delete category with existing transactions."

7. **Summary view**
   - Dashboard displays three summary cards above the transaction list:
     - Total Income: sum of all income transactions (current filtered set or all transactions)
     - Total Expenses: sum of all expense transactions
     - Net Balance: Total Income minus Total Expenses
   - Cards update dynamically when filters change.
   - Amounts display with currency formatting ($X,XXX.XX).

8. **Database schema enforcement**
   - PostgreSQL schema with transactions and categories tables as specified.
   - transactions.type and categories.type have CHECK constraints enforcing 'income' or 'expense' only.
   - transactions.category_id has FOREIGN KEY constraint to categories.id with ON DELETE RESTRICT to prevent orphaning.
   - categories.name has UNIQUE constraint.
   - transactions.amount is DECIMAL(10,2) ensuring two decimal place precision.

### Explicitly not MVP (v0.1)

- User authentication or multi-user support (single-user application)
- Recurring transactions or scheduled entries
- Bulk import/export (CSV, Excel)
- Budget tracking or spending limits
- Reporting or analytics beyond summary totals (charts, graphs, trends)
- Attachments or receipt uploads
- Currency selection or multi-currency support (assumes USD)
- Mobile native application
- Real-time collaboration or syncing
- Audit logs showing who changed what when (beyond created_at timestamp)
- Search functionality (filtering is provided, not free-text search)
- Subcategories or hierarchical categories
- Tagging system beyond categories

---

## 3) Hard boundaries (anti-godfile rules)

### API Routes (presentation layer)
- Parse HTTP request body, query parameters, and path parameters.
- Call appropriate service method with validated data.
- Return HTTP response with proper status code and JSON body.
- MUST NOT contain business logic, database queries, data validation beyond HTTP-level checks, or direct database imports.
- MUST NOT perform calculations, enforce business rules, or manipulate transaction data.

### Services (business logic layer)
- Orchestrate transaction and category operations: create, update, delete, retrieve, filter.
- Compute summary totals (total income, total expenses, net balance).
- Enforce business rules: category existence validation, deletion restrictions.
- MUST NOT import FastAPI, Pydantic request models, or HTTP response classes.
- MUST NOT contain SQL queries, database connection logic, or ORM model imports.
- MUST NOT import React components or frontend code.

### Repositories (data access layer)
- All database reads and writes using SQLAlchemy ORM or raw SQL.
- CRUD operations for transactions and categories tables.
- Query filtering by type, category, date range.
- MUST NOT contain business logic, HTTP concerns, or validation beyond database-level constraints.
- MUST NOT call service methods or import service modules.
- MUST NOT format data for presentation (currency formatting, date formatting).

### Models (data structures)
- SQLAlchemy ORM models mapping to transactions and categories tables.
- Pydantic schemas for API request/response validation.
- MUST NOT contain business logic, database queries, or HTTP handling.
- MUST define exact column types, constraints, and relationships as per schema specification.

### Frontend Components (UI layer)
- React components for rendering transaction list, filters, forms, summary cards, category management.
- Handle user interactions, form submissions, button clicks.
- MUST NOT contain direct API calls (use API client services).
- MUST NOT contain business logic or data transformation beyond UI state management.

### Frontend API Client (data fetching layer)
- HTTP client wrapper for all backend API calls.
- Methods for each endpoint: createTransaction, getTransactions, updateTransaction, deleteTransaction, createCategory, getCategories, etc.
- MUST NOT contain UI rendering logic, React hooks, or component code.
- MUST NOT contain business logic or data validation (validation happens on backend).

### Frontend State Management (application state layer)
- Manage global or shared state for transactions, categories, filters, summary data.
- MUST NOT contain API calls (use API client) or UI rendering logic.
- MUST NOT contain business logic beyond state updates.

---

## 4) Deployment target

- Target: Local development environment (initial build), Render web service (future production)
- Database: Neon PostgreSQL (managed, serverless)
- Backend: Python/FastAPI application running on Render as a single web service process
- Frontend: React/TypeScript application built with Vite, served as static files from Render or separate static hosting
- Expected users: 1-10 initially (single-user or small team usage)
- No CI/CD pipeline required for MVP. Manual deployment via Render dashboard or CLI.
- No containerization (Docker) required for MVP. Render handles process management.
- Application must support environment variables for database connection string (Neon connection URL) and any configuration.
- Frontend must make API calls to backend via configurable base URL (environment variable) to support local development (localhost:8000) and production (Render URL).