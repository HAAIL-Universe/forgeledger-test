# ForgeLedger Test — Phases

Canonical phase plan. Each phase is self-contained, shippable, and auditable. The builder contract (S1) requires completing phases in strict order. No phase may begin until the previous phase passes audit.

---

## Phase 0 — Genesis

**Objective:** Skeleton project that boots, passes lint, has one test, and serves health endpoint.

**Deliverables:**
- Project structure matching clean architecture layers:
  - `backend/` — Python FastAPI application
    - `api/` — presentation layer (routes)
    - `services/` — business logic layer
    - `repositories/` — data access layer
    - `models/` — Pydantic models and domain entities
    - `database.py` — PostgreSQL connection manager
  - `frontend/` — React TypeScript application (Vite)
    - `src/components/` — UI components
    - `src/services/` — API client services
    - `src/types/` — TypeScript interfaces
  - `migrations/` — Alembic database migrations
- `boot.ps1` — installs backend deps (Python venv), frontend deps (npm), starts PostgreSQL connection test, starts uvicorn dev server
- `backend/main.py` — FastAPI app with `/health` endpoint returning `{ "status": "ok", "database": "connected" }`
- `backend/database.py` — SQLAlchemy async engine configured for Neon PostgreSQL
- `backend/requirements.txt` — FastAPI, SQLAlchemy, asyncpg, alembic, pytest, pytest-asyncio
- `frontend/package.json` — React, TypeScript, Vite, Vitest, React Router
- `pytest` passes with one health endpoint test
- `vitest` passes with one component smoke test
- `.env.example` — template for DATABASE_URL, CORS_ORIGINS
- `.gitignore` — Python venv, node_modules, .env, __pycache__, dist
- `forge.json` — project metadata with phase tracking

**Schema coverage:**
- Database connection established, no tables yet

**Exit criteria:**
- `boot.ps1` runs without errors and starts both backend and frontend dev servers
- `GET /health` returns 200 with database connection confirmed
- `pytest` passes (1 backend test)
- `npm run test` passes (1 frontend test)
- Environment variable validation fails gracefully with clear error messages
- `run_audit.ps1` passes all checks

---

## Phase 1 — Categories Foundation

**Objective:** Implement category management as the foundation for transaction categorization.

**Deliverables:**
- Alembic migration creating `categories` table:
  - `id` UUID PRIMARY KEY (default gen_random_uuid())
  - `name` VARCHAR(100) NOT NULL UNIQUE
  - `type` VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense'))
- `backend/models/category.py` — Pydantic models:
  - `CategoryCreate` (name, type)
  - `CategoryUpdate` (name, type — both optional)
  - `CategoryResponse` (id, name, type)
- `backend/repositories/category_repository.py` — data layer:
  - `create_category(db, category_data)` — insert with duplicate name handling
  - `get_all_categories(db, type_filter=None)` — list with optional type filter
  - `get_category_by_id(db, category_id)` — fetch single category
  - `update_category(db, category_id, category_data)` — update with validation
  - `delete_category(db, category_id)` — delete with foreign key constraint check
- `backend/services/category_service.py` — business logic:
  - Validation: name required, type must be 'income' or 'expense'
  - Business rule: cannot delete category if transactions reference it
  - Default categories seeded: "Salary" (income), "Groceries" (expense), "Utilities" (expense), "Freelance" (income)
- `backend/api/categories.py` — REST routes:
  - `POST /api/categories` — create category
  - `GET /api/categories` — list all categories (with optional ?type= filter)
  - `PUT /api/categories/{id}` — update category
  - `DELETE /api/categories/{id}` — delete category
- `frontend/src/types/category.ts` — TypeScript interfaces matching backend models
- `frontend/src/services/categoryService.ts` — API client for all category operations
- `frontend/src/components/CategoryManager.tsx` — UI for category CRUD:
  - List view with income/expense tabs
  - Add category form (modal)
  - Inline edit capability
  - Delete confirmation dialog
- Comprehensive test coverage:
  - Pytest tests for all repository methods
  - Pytest tests for service layer business rules
  - Pytest tests for API endpoints (success and error cases)
  - Vitest tests for CategoryManager component

**Schema coverage:**
- [x] `categories` table (id, name, type)

**Exit criteria:**
- All API endpoints return correct status codes (200, 201, 400, 404, 409)
- Cannot create duplicate category names (409 Conflict)
- Cannot delete category if referenced by transactions (400 Bad Request with helpful message)
- Default categories seeded on first migration
- Type filter works correctly (GET /api/categories?type=income)
- Frontend component renders category list grouped by type
- All tests pass (pytest + vitest)
- `run_audit.ps1` passes all checks

---

## Phase 2 — Transactions Core

**Objective:** Implement transaction logging with full CRUD operations and category relationships.

**Deliverables:**
- Alembic migration creating `transactions` table:
  - `id` UUID PRIMARY KEY (default gen_random_uuid())
  - `amount` DECIMAL(10,2) NOT NULL CHECK (amount > 0)
  - `type` VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense'))
  - `category_id` UUID FOREIGN KEY REFERENCES categories(id) ON DELETE RESTRICT
  - `date` DATE NOT NULL (default CURRENT_DATE)
  - `description` TEXT (nullable)
  - `created_at` TIMESTAMP DEFAULT NOW()
  - Index on `date` for performance
  - Index on `category_id` for joins
- `backend/models/transaction.py` — Pydantic models:
  - `TransactionCreate` (amount, type, category_id, date, description)
  - `TransactionUpdate` (all fields optional)
  - `TransactionResponse` (id, amount, type, category_id, category_name, date, description, created_at)
- `backend/repositories/transaction_repository.py` — data layer:
  - `create_transaction(db, transaction_data)` — insert with foreign key validation
  - `get_all_transactions(db, filters)` — list with filtering:
    - `type` (income/expense)
    - `category_id` (UUID)
    - `start_date` / `end_date` (date range)
    - Default sort: date DESC, created_at DESC
  - `get_transaction_by_id(db, transaction_id)` — fetch with category join
  - `update_transaction(db, transaction_id, transaction_data)` — update with validation
  - `delete_transaction(db, transaction_id)` — delete by ID
  - `get_balance_summary(db, filters)` — aggregate totals (total_income, total_expense, net_balance)
- `backend/services/transaction_service.py` — business logic:
  - Validation: amount must be positive, date cannot be future, category must exist and match type
  - Business rule: category type must match transaction type
  - Business rule: date validation (not future, reasonable past limit)
  - Enrichment: attach category name to transaction responses
- `backend/api/transactions.py` — REST routes:
  - `POST /api/transactions` — create transaction
  - `GET /api/transactions` — list with query params (?type=, ?category_id=, ?start_date=, ?end_date=)
  - `GET /api/transactions/{id}` — get single transaction
  - `PUT /api/transactions/{id}` — update transaction
  - `DELETE /api/transactions/{id}` — delete transaction
  - `GET /api/transactions/summary` — get balance summary (filtered)
- `frontend/src/types/transaction.ts` — TypeScript interfaces
- `frontend/src/services/transactionService.ts` — API client for all transaction operations
- `frontend/src/components/TransactionForm.tsx` — Add/Edit form:
  - Amount input (numeric, 2 decimal places)
  - Type selector (income/expense radio buttons)
  - Category dropdown (filtered by selected type)
  - Date picker (defaults to today)
  - Description textarea
  - Form validation with helpful error messages
- `frontend/src/components/TransactionList.tsx` — Transaction table:
  - Columns: Date, Description, Category, Type, Amount
  - Color coding: green for income, red for expense
  - Click row to edit
  - Delete button with confirmation
  - Empty state for no transactions
- Comprehensive test coverage:
  - Pytest tests for repository layer (all CRUD operations)
  - Pytest tests for service layer (validation rules)
  - Pytest tests for API endpoints (success and error paths)
  - Pytest test for category type mismatch prevention
  - Vitest tests for TransactionForm validation
  - Vitest tests for TransactionList rendering

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (id, amount, type, category_id, date, description, created_at)

**Exit criteria:**
- Cannot create transaction with category type mismatch (400 Bad Request)
- Cannot create transaction with non-existent category (404 Not Found)
- Amount validation prevents negative or zero values
- Date validation prevents future dates
- Foreign key constraint prevents category deletion when transactions exist
- Transaction list returns results sorted by date (newest first)
- All filters work correctly (type, category, date range)
- Summary endpoint returns correct totals
- All tests pass (pytest + vitest)
- `run_audit.ps1` passes all checks

---

## Phase 3 — Dashboard & Filtering

**Objective:** Build the main dashboard with transaction filtering, search, and summary views.

**Deliverables:**
- `frontend/src/pages/Dashboard.tsx` — Main application view:
  - Page layout: header, filter sidebar, transaction list, summary panel
  - Responsive design: sidebar collapses to drawer on mobile (<768px)
- `frontend/src/components/FilterPanel.tsx` — Transaction filters:
  - Type filter: All / Income / Expense (toggle buttons)
  - Category filter: multi-select dropdown (grouped by type)
  - Date range filter: start/end date pickers with presets (Today, This Week, This Month, This Year, Custom)
  - Clear all filters button
  - Active filter count badge
  - Filter state persisted to URL query params
- `frontend/src/components/SummaryPanel.tsx` — Financial summary:
  - Total Income (green)
  - Total Expense (red)
  - Net Balance (green if positive, red if negative)
  - Summary respects active filters
  - Visual indicator: progress bar showing expense ratio
  - Month-over-month comparison (if date filter is single month)
- `frontend/src/components/TransactionTable.tsx` — Enhanced table:
  - Pagination (25 per page)
  - Sortable columns (date, amount)
  - Search bar (filters by description)
  - Bulk actions: select multiple, delete selected
  - Export button (downloads CSV — Phase 4 implementation)
  - Loading states with skeleton loaders
  - Hover actions: quick edit, duplicate, delete
- `frontend/src/hooks/useTransactions.ts` — Custom hook:
  - Manages transaction list state
  - Handles filtering, pagination, sorting
  - Debounced search (300ms)
  - Optimistic updates for delete operations
- `frontend/src/utils/formatters.ts` — Utility functions:
  - `formatCurrency(amount)` — locale-aware formatting
  - `formatDate(date)` — consistent date display
  - `parseFilterParams(searchParams)` — URL param parsing
- Category-based color coding throughout UI:
  - Each category gets consistent color assignment
  - Color palette: 8 distinct colors for visual differentiation
- Empty states for all views:
  - No transactions: "Add your first transaction" with CTA button
  - No results: "No transactions match your filters" with clear filters button
  - No categories: "Create categories first" with link to category manager
- Comprehensive test coverage:
  - Vitest tests for FilterPanel state management
  - Vitest tests for SummaryPanel calculations
  - Vitest tests for TransactionTable sorting and pagination
  - Vitest tests for useTransactions hook
  - Vitest tests for formatter utilities

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- Dashboard loads and displays all transactions on initial render
- All filters work correctly and can be combined
- Filter state syncs with URL (shareable filtered views)
- Summary panel updates in real-time as filters change
- Pagination works correctly (page state preserved during filter changes)
- Search debouncing works (no API call until typing stops)
- Table sorting works for date and amount columns
- Empty states render correctly for all scenarios
- Mobile responsive: sidebar becomes drawer, table becomes card list
- All tests pass (vitest)
- `run_audit.ps1` passes all checks

---

## Phase 4 — Data Import/Export

**Objective:** Enable users to import transactions from CSV and export data for backup or analysis.

**Deliverables:**
- `backend/services/import_service.py` — CSV import logic:
  - Parse CSV with validation: required columns (date, amount, type, category_name, description)
  - Map category names to IDs (case-insensitive matching)
  - Validation: amount format, type values, date format (ISO 8601 or common formats)
  - Error handling: collect all validation errors, return detailed error report
  - Batch insert: use transaction for atomicity (all or nothing)
  - Dry-run mode: validate without inserting
- `backend/services/export_service.py` — CSV export logic:
  - Query transactions with filters (reuse transaction repository filtering)
  - Format as CSV: Date, Description, Category, Type, Amount
  - Stream large datasets (don't load all into memory)
  - Filename convention: `forgeledger_export_YYYY-MM-DD.csv`
- `backend/api/import_export.py` — REST routes:
  - `POST /api/transactions/import` — upload CSV (multipart/form-data)
    - Query param `?dry_run=true` for validation only
    - Returns: `{ "success": true, "imported": 45, "errors": [] }` or error details
  - `GET /api/transactions/export` — download CSV
    - Accepts same filter query params as GET /api/transactions
    - Returns CSV file with appropriate headers
- `frontend/src/components/ImportDialog.tsx` — Import modal:
  - File upload (drag-and-drop or click to browse)
  - CSV template download link (example format)
  - Dry-run preview: show validation results before import
  - Progress indicator during upload
  - Success summary: "45 transactions imported successfully"
  - Error display: table of rows with validation errors
- `frontend/src/components/ExportButton.tsx` — Export component:
  - Export button in dashboard toolbar
  - Dropdown menu: Export All / Export Filtered
  - Progress indicator for large exports
  - Success notification with file download
- CSV template generation:
  - `GET /api/transactions/template` — download empty template with headers and example rows
- Validation rules for import:
  - Amount must be positive decimal
  - Type must be "income" or "expense" (case-insensitive)
  - Date must be valid format (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
  - Category must exist (create missing categories option)
  - Description is optional
- Comprehensive test coverage:
  - Pytest tests for CSV parsing with various formats
  - Pytest tests for validation error collection
  - Pytest tests for batch import transaction handling
  - Pytest tests for export with filters
  - Vitest tests for ImportDialog file upload
  - Vitest tests for validation error display

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- Can upload valid CSV and import all transactions
- Validation errors are detailed and actionable (row number, column, error message)
- Dry-run mode shows what would be imported without committing
- Export respects active filters
- Export file opens correctly in Excel/Google Sheets
- Large imports (1000+ rows) complete without timeout
- Import is atomic: failures don't leave partial data
- Template download provides clear example format
- All tests pass (pytest + vitest)
- `run_audit.ps1` passes all checks

---

## Phase 5 — Analytics & Insights

**Objective:** Provide visual insights into spending patterns, category breakdowns, and trends over time.

**Deliverables:**
- `backend/services/analytics_service.py` — Analytics calculations:
  - `get_category_breakdown(db, filters)` — spending by category (amount, percentage)
  - `get_monthly_trends(db, start_date, end_date)` — time series data (month, income, expense, net)
  - `get_top_expenses(db, limit, filters)` — largest expense transactions
  - `get_spending_patterns(db)` — average daily/weekly/monthly spending
- `backend/api/analytics.py` — REST routes:
  - `GET /api/analytics/category-breakdown` — category breakdown (filtered)
  - `GET /api/analytics/trends` — monthly trend data (date range required)
  - `GET /api/analytics/top-expenses` — top N largest expenses
  - `GET /api/analytics/patterns` — spending pattern summary
- `frontend/src/pages/AnalyticsPage.tsx` — Analytics dashboard:
  - Page layout: grid of chart cards
  - Date range selector (affects all charts)
- `frontend/src/components/charts/CategoryBreakdownChart.tsx` — Pie/Donut chart:
  - Shows spending by category
  - Interactive: click slice to filter transactions
  - Percentage labels
  - Legend with category colors
- `frontend/src/components/charts/TrendChart.tsx` — Line chart:
  - Income and expense trends over time
  - Dual Y-axis or stacked area visualization
  - Tooltip shows exact values
  - Net balance line (optional toggle)
- `frontend/src/components/charts/TopExpensesCard.tsx` — Bar chart:
  - Horizontal bars for top 10 expenses
  - Click bar to view transaction detail
  - Shows transaction description and amount
- `frontend/src/components/InsightsSummary.tsx` — Key metrics cards:
  - Average daily spending
  - Largest expense this month
  - Most used category
  - Spending trend indicator (up/down compared to last period)
- Chart library integration:
  - Install Chart.js or Recharts (React-friendly charting library)
  - Responsive chart sizing
  - Consistent color scheme matching category colors
- Loading states for all analytics components
- Empty states: "Not enough data for insights. Add more transactions."
- Comprehensive test coverage:
  - Pytest tests for all analytics calculations
  - Pytest tests for analytics API endpoints
  - Pytest tests for edge cases (no data, single transaction, date ranges)
  - Vitest tests for chart rendering
  - Vitest tests for chart interactions (click handlers)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- Category breakdown accurately represents spending distribution
- Trend chart shows correct income/expense over time
- Top expenses list shows largest transactions with correct amounts
- All charts are responsive and render correctly on mobile
- Chart interactions work (click to filter, tooltips)
- Date range selector updates all charts simultaneously
- Analytics calculations handle edge cases (no data, single month, etc.)
- All tests pass (pytest + vitest)
- `run_audit.ps1` passes all checks

---

## Phase 6 — Performance & Optimization

**Objective:** Optimize database queries, implement caching, and ensure the application performs well with large datasets.

**Deliverables:**
- Database optimization:
  - Composite index on `transactions(date, type)` for common filtered queries
  - Analyze query plans for slow queries (EXPLAIN ANALYZE)
  - Connection pooling configuration (SQLAlchemy pool_size, max_overflow)
- Backend caching layer:
  - In-memory cache for category list (rarely changes, frequently queried)
  - Cache decorator utility for service methods
  - Cache invalidation on category create/update/delete
  - Response caching for analytics endpoints (5-minute TTL)
- API response optimization:
  - Pagination for all list endpoints (default 25, max 100)
  - Partial response support: `?fields=id,amount,date` to reduce payload size
  - ETag support for transaction list (cache validation)
  - Compression: gzip response encoding for payloads > 1KB
- Frontend performance:
  - React.memo for expensive components (TransactionList, charts)
  - Virtualized scrolling for transaction table (react-window)
  - Lazy loading: code-split analytics page
  - Debounced search and filter inputs
  - Optimistic UI updates (update UI before API confirms)
- `backend/middleware/performance.py` — Performance monitoring:
  - Request timing middleware (log slow requests > 500ms)
  - Database query counter (detect N+1 queries in development)
  - Response size logging
- Load testing scripts:
  - `scripts/load_test.py` — pytest-based load test generating 10,000 transactions
  - `scripts/benchmark.py` — measure API response times for common operations
- Performance budgets:
  - Dashboard initial load: < 2 seconds
  - Transaction list load (25 items): < 500ms
  - Filter/search response: < 300ms
  - Analytics page load: < 1 second
  - Import 1000 transactions: < 10 seconds
- Monitoring and logging:
  - Structured logging (JSON format)
  - Error tracking with stack traces
  - Performance metrics logged per request
  - Database query logging in development (disabled in production)
- Comprehensive test coverage:
  - Pytest tests for caching behavior
  - Pytest tests for pagination edge cases
  - Load tests validate performance budgets
  - Vitest tests for virtualized scrolling
  - Vitest tests for optimistic updates

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2) + performance indexes

**Exit criteria:**
- All performance budgets met with 10,000 transactions in database
- No N+1 queries detected in query logs
- Dashboard loads in < 2 seconds with full dataset
- Transaction list scrolling is smooth (60fps)
- Analytics calculations complete in < 1 second
- Caching reduces repeated query load (verify with metrics)
- Load tests pass without errors or timeouts
- All tests pass (pytest + vitest)
- `run_audit.ps1` passes all checks

---

## Phase 7 — Error Handling & Validation

**Objective:** Comprehensive error handling, input validation, and user-friendly error messages throughout the application.

**Deliverables:**
- `backend/exceptions.py` — Custom exception hierarchy:
  - `AppException` (base)
  - `ValidationError` (400)
  - `NotFoundError` (404)
  - `ConflictError` (409)
  - `DatabaseError` (500)
- `backend/middleware/error_handler.py` — Global error handler:
  - Catches all exceptions
  - Returns consistent error response format: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": {...} } }`
  - Logs errors with context (user action, request ID, stack trace)
  - Never exposes internal errors to client (sanitize 500 responses)
- Backend validation layer:
  - Pydantic model validation for all API inputs
  - Custom validators: date range, amount precision, enum values
  - Cross-field validation: category type matches transaction type
  - Database constraint validation: unique names, foreign keys
- `backend/services/validation_service.py` — Business rule validation:
  - `validate_transaction_data()` — all transaction business rules
  - `validate_category_data()` — category name uniqueness, type validity
  - `validate_date_range()` — start <= end, not too far in past/future
  - Returns detailed error objects with field-level messages
- Frontend validation:
  - Form-level validation: Zod schemas matching backend models
  - Field-level validation: real-time feedback as user types
  - Display validation errors inline (below input fields)
  - Disable submit button until form is valid
- `frontend/src/utils/errorHandler.ts` — Client-side error handling:
  - Parse API error responses
  - Display user-friendly error messages (toast notifications)
  - Map error codes to user messages
  - Retry logic for network errors
  - Fallback error messages for unknown errors
- `frontend/src/components/ErrorBoundary.tsx` — React error boundary:
  - Catches render errors
  - Displays fallback UI with error message
  - "Report issue" button (logs error details)
  - "Reload page" button to recover
- Error message catalog:
  - `frontend/src/constants/errorMessages.ts` — centralized error messages
  - User-friendly messages for all error codes
  - Actionable instructions ("Check your internet connection", "Please try again")
- Input sanitization:
  - Backend: strip HTML tags from text inputs, escape SQL (parameterized queries)
  - Frontend: sanitize display of user-generated content (DOMPurify)
- Rate limiting:
  - API rate limiting middleware (10 requests/second per IP)
  - Return 429 Too Many Requests with Retry-After header
- Comprehensive test coverage:
  - Pytest tests for all validation functions
  - Pytest tests for error handler middleware
  - Pytest tests for rate limiting
  - Vitest tests for form validation
  - Vitest tests for ErrorBoundary
  - Vitest tests for error message display

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- All API endpoints return consistent error format
- Frontend displays user-friendly error messages (never raw API errors)
- Form validation provides real-time feedback
- Invalid inputs are rejected at all layers (frontend, API, database)
- Error logs contain sufficient context for debugging
- Rate limiting prevents abuse (verified with load test)
- Error boundary catches render errors gracefully
- All validation rules documented in test cases
- All tests pass (pytest + vitest)
- `run_audit.ps1` passes all checks

---

## Phase 8 — Ship & Deploy

**Objective:** Final hardening, comprehensive documentation, deployment readiness, and production infrastructure setup.

**Deliverables:**
- **Comprehensive README.md:**
  - Project overview and key features
  - Technology stack (Python FastAPI, React TypeScript, PostgreSQL, Neon, Render)
  - Prerequisites: Python 3.11+, Node.js 18+, PostgreSQL 14+
  - Local setup instructions:
    - Clone repository
    - Set up environment variables (`.env` file)
    - Install dependencies (`boot.ps1` or manual steps)
    - Run database migrations
    - Start backend and frontend dev servers
  - Environment variables reference:
    - `DATABASE_URL` — PostgreSQL connection string (Neon)
    - `CORS_ORIGINS` — allowed frontend origins
    - `SECRET_KEY` — for future session management
  - Usage guide:
    - Creating categories
    - Adding transactions
    - Using filters and search
    - Exporting/importing data
    - Viewing analytics
  - API reference:
    - All endpoints with method, path, request/response examples
    - Error codes and meanings
  - Development guide:
    - Running tests (`pytest`, `npm run test`)
    - Code structure and architecture
    - Adding new features
  - Deployment guide:
    - Render setup (backend and frontend)
    - Neon PostgreSQL configuration
    - Environment variable setup in Render
  - Troubleshooting section (common issues and solutions)
  - License and contribution guidelines
- `boot.ps1` — One-click full setup:
  - Check prerequisites (Python, Node, Git)
  - Create Python venv and install dependencies
  - Install frontend dependencies
  - Check for `.env` file (prompt to create if missing)
  - Run database migrations
  - Start backend server (background process)
  - Start frontend dev server (foreground)
  - Print success message with URLs
- `USER_INSTRUCTIONS.md` — End-user guide:
  - What is ForgeLedger Test
  - Getting started (account not needed, local-first)
  - How to add your first transaction
  - Understanding categories
  - Using filters to find transactions
  - Interpreting analytics charts
  - Importing transactions from CSV (with example file)
  - Exporting data for backup
  - Tips for effective financial tracking
  - FAQ section
- Deployment configuration:
  - `render.yaml` — Render blueprint:
    - Backend service: Python 3.11, `uvicorn main:app --host 0.0.0.0`
    - Frontend service: Node 18, `npm run build`, static site
    - Environment variables configured
    - Health check endpoints
  - `backend/Dockerfile` (optional, if using Docker):
    - Multi-stage build for smaller image
    - Production dependencies only
    - Non-root user
  - `frontend/Dockerfile` (optional):
    - Build step with Vite
    - Serve with nginx
- Production hardening:
  - Environment variable validation on startup (fail fast)
  - Graceful shutdown handlers (SIGTERM, SIGINT)
  - Database connection retry logic with exponential backoff
  - Request timeout enforcement (30 seconds)
  - CORS configuration locked down to production frontend URL
  - Security headers: CSP, X-Frame-Options, HSTS
  - SQL injection prevention audit (all queries use parameterization)
  - XSS prevention audit (all user inputs sanitized)
- Final testing suite:
  - Full integration test: create category, create transaction, filter, export
  - End-to-end test: simulate user workflow in frontend
  - Performance test: load 10,000 transactions, verify response times
  - Security test: attempt common attacks (SQL injection, XSS)
- Monitoring and observability:
  - Health check endpoint with database ping
  - `/metrics` endpoint (optional: Prometheus-compatible metrics)
  - Structured logging to stdout (JSON format for log aggregation)
  - Error rate tracking
- `scripts/seed_demo_data.py` — Demo data generator:
  - Creates realistic demo dataset (100 transactions across 3 months)
  - Useful for testing and screenshots
- Production checklist:
  - [ ] All tests pass (pytest + vitest)
  - [ ] `run_audit.ps1` passes all checks
  - [ ] README.md is complete and accurate
  - [ ] USER_INSTRUCTIONS.md is beginner-friendly
  - [ ] Environment variables documented
  - [ ] Render deployment tested (staging environment)
  - [ ] Database migrations run successfully on Neon
  - [ ] Frontend builds without errors
  - [ ] Health check endpoint returns 200
  - [ ] Error logging works in production
  - [ ] CORS is properly configured
  - [ ] Security headers are set
  - [ ] Performance budgets met in production environment
- Comprehensive test coverage:
  - Pytest integration tests for full workflows
  - Vitest E2E tests (Playwright or Cypress)
  - Security tests for common vulnerabilities
  - Load tests validate production readiness

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- `boot.ps1` successfully sets up the entire project from a fresh clone
- README.md covers all setup, usage, and deployment steps
- USER_INSTRUCTIONS.md enables non-technical users to use the application
- Application deploys successfully to Render (backend and frontend)
- Health check returns 200 in production
- Database connection works with Neon PostgreSQL
- All environment variables are documented and validated
- No security vulnerabilities detected (OWASP Top 10 checked)
- All tests pass (pytest + vitest + E2E)
- Performance budgets met in production
- Error logging captures all exceptions with context
- `run_audit.ps1` passes all checks
- Project is production-ready and maintainable

---

**END OF PHASES CONTRACT**