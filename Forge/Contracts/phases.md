# ForgeLedger Test — Phases

Canonical phase plan. Each phase is self-contained, shippable, and auditable. The builder contract (S1) requires completing phases in strict order. No phase may begin until the previous phase passes audit.

---

## Phase 0 — Genesis

**Objective:** Bootstrap project skeleton with working health endpoint, database connection, and essential tooling. Establish foundational project structure that matches architectural boundaries.

**Deliverables:**
- Project root structure with backend (`/backend`) and frontend (`/frontend`) directories
- Backend: FastAPI application with `/health` endpoint returning `{ "status": "ok", "database": "connected" }`
- Database: PostgreSQL connection to Neon with connection pooling (asyncpg)
- Database migrations setup using Alembic
- Frontend: Vite + React + TypeScript skeleton with basic routing
- Root `boot.ps1` — installs backend deps (Poetry/pip), installs frontend deps (npm), runs DB migrations, starts uvicorn and Vite dev server concurrently
- `pytest` setup with one health endpoint test
- `vitest` setup with one component smoke test
- Backend layered structure: `/routes` (API), `/services` (business logic), `/repositories` (data access), `/models` (schemas)
- Frontend structure: `/components` (UI), `/services` (API client), `/hooks` (state management), `/types` (TypeScript definitions)
- `forge.json` at project root with initial phase metadata
- `.gitignore` for Python, Node, and IDE artifacts
- `.env.example` with required environment variables (DATABASE_URL, API_PORT, etc.)
- ESLint and Prettier configuration for frontend
- Black and isort configuration for backend

**Schema coverage:**
- Database connection established (no tables yet)

**Exit criteria:**
- `boot.ps1` runs without errors on fresh clone
- `GET /health` returns 200 with database connection status
- `pytest` passes (1 backend test)
- `vitest` passes (1 frontend test)
- Database connection succeeds to Neon instance
- Alembic migrations directory created and initialized
- Frontend dev server starts and renders placeholder homepage
- `run_audit.ps1` passes all checks

---

## Phase 1 — Category Management

**Objective:** Implement complete category CRUD operations with backend layering and frontend UI. Categories are foundational for transaction classification.

**Deliverables:**
- Database migration: `categories` table (id UUID PRIMARY KEY, name VARCHAR(100) NOT NULL UNIQUE, type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')))
- Repository layer: `CategoryRepository` class with methods: `create()`, `get_all()`, `get_by_id()`, `update()`, `delete()`, `get_by_type()`
- Service layer: `CategoryService` class with business logic for category validation, duplicate checking, and safe deletion (verify no transactions reference category)
- API routes:
  - `POST /categories` — create new category with validation (name required, type must be 'income' or 'expense')
  - `GET /categories` — list all categories with optional type filter
  - `GET /categories?type=income` — filter categories by type
  - `PUT /categories/{id}` — update category (name and/or type)
  - `DELETE /categories/{id}` — delete category (fails with 409 if transactions exist)
- Pydantic models: `CategoryCreate`, `CategoryUpdate`, `CategoryResponse`
- Frontend API client: `categoryService.ts` with typed methods for all category operations
- Frontend components:
  - `CategoryList` — displays all categories grouped by type (income/expense)
  - `CategoryForm` — modal form for create/edit with validation
  - `CategoryCard` — individual category display with edit/delete actions
- Frontend pages:
  - `CategoriesPage` — full category management interface
- Error handling: proper HTTP status codes, validation error messages
- Unit tests for repository layer (5 tests)
- Unit tests for service layer (8 tests covering validation and edge cases)
- Integration tests for API endpoints (9 tests)
- Frontend component tests for form and list (4 tests)

**Schema coverage:**
- [x] `categories` table

**Exit criteria:**
- All CRUD operations work through API
- Cannot create duplicate category names
- Cannot delete category if transactions reference it
- Type filter correctly separates income and expense categories
- Frontend form validates required fields before submission
- All backend tests pass (pytest: 22 tests)
- All frontend tests pass (vitest: 4 tests)
- API returns proper error messages for validation failures
- `run_audit.ps1` passes all checks

---

## Phase 2 — Transaction Core

**Objective:** Implement transaction CRUD with proper layering, category relationships, and type validation. This is the heart of the ledger system.

**Deliverables:**
- Database migration: `transactions` table (id UUID PRIMARY KEY, amount DECIMAL(10,2) NOT NULL, type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')), category_id UUID FOREIGN KEY REFERENCES categories(id), date DATE NOT NULL, description TEXT, created_at TIMESTAMP DEFAULT NOW())
- Repository layer: `TransactionRepository` class with methods: `create()`, `get_all()`, `get_by_id()`, `update()`, `delete()`, `get_by_filters()`, `get_summary_stats()`
- Service layer: `TransactionService` class with business logic:
  - Validate amount is positive
  - Validate category exists and matches transaction type (income transaction must use income category)
  - Validate date is not in future
  - Calculate running balance
  - Generate summary statistics (total income, total expenses, net balance)
- API routes:
  - `POST /transactions` — create transaction with full validation
  - `GET /transactions` — list all transactions with pagination (default 50 per page)
  - `GET /transactions?type=income` — filter by transaction type
  - `GET /transactions?category_id={uuid}` — filter by category
  - `GET /transactions?start_date={date}&end_date={date}` — filter by date range
  - `GET /transactions?type=income&start_date=2024-01-01&end_date=2024-12-31` — combined filters
  - `GET /transactions/{id}` — get single transaction with category details
  - `PUT /transactions/{id}` — update transaction with same validation as create
  - `DELETE /transactions/{id}` — soft or hard delete (configurable)
  - `GET /transactions/summary` — return total income, total expenses, net balance
- Pydantic models: `TransactionCreate`, `TransactionUpdate`, `TransactionResponse` (includes nested category), `TransactionSummary`
- Database indexes: `idx_transactions_date`, `idx_transactions_type`, `idx_transactions_category_id` for query performance
- Query optimization: eager loading of category data to avoid N+1 queries
- Unit tests for repository layer (8 tests)
- Unit tests for service layer (15 tests covering all validation rules and edge cases)
- Integration tests for API endpoints (18 tests covering all filter combinations)
- Test data fixtures: seed categories and transactions for testing

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table

**Exit criteria:**
- All CRUD operations work through API
- Cannot create transaction with amount <= 0
- Cannot create income transaction with expense category (and vice versa)
- Cannot create transaction with non-existent category
- Cannot create transaction with future date
- All filter combinations work correctly
- Pagination returns correct page size and total count
- Summary endpoint calculates correct totals
- Database indexes are created and used by queries
- All backend tests pass (pytest: 41 tests)
- `run_audit.ps1` passes all checks

---

## Phase 3 — Transaction UI & Filters

**Objective:** Build comprehensive transaction interface with filtering, sorting, and summary display. Make the ledger immediately useful.

**Deliverables:**
- Frontend API client: `transactionService.ts` with typed methods for all transaction operations and filter combinations
- Frontend state management: Custom hooks for transaction data (`useTransactions`, `useTransactionFilters`, `useTransactionSummary`)
- Frontend components:
  - `TransactionList` — table view with columns: Date, Description, Category, Type, Amount
  - `TransactionRow` — individual row with edit/delete actions
  - `TransactionForm` — modal form for create/edit with category dropdown (filtered by type)
  - `TransactionFilters` — filter panel with: type toggle, category dropdown, date range picker
  - `TransactionSummary` — summary cards showing total income (green), total expenses (red), net balance (dynamic color)
  - `EmptyState` — helpful message when no transactions match filters
- Frontend pages:
  - `DashboardPage` — main view combining summary, filters, and transaction list
- UI features:
  - Real-time summary updates as filters change
  - Visual distinction between income (green) and expense (red) amounts
  - Sortable columns (date, amount)
  - Category badges with color coding
  - Responsive table (stacks on mobile)
  - Loading skeletons during data fetch
  - Error toast notifications
- Form validation:
  - Amount must be positive number with 2 decimal places
  - Date required and cannot be future
  - Category required and filtered by transaction type
  - Description optional but trimmed
- Date range picker integration (react-datepicker or similar)
- Pagination controls (Previous/Next with page info)
- Optimistic UI updates for create/update/delete
- Frontend component tests (12 tests covering form, filters, list, summary)
- Integration tests with mock API (8 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- User can view all transactions in table format
- User can create transaction with form validation
- User can edit transaction with pre-filled form
- User can delete transaction with confirmation dialog
- Filters update transaction list in real-time
- Summary shows correct totals for filtered transactions
- Category dropdown only shows categories matching transaction type
- Amount input enforces 2 decimal places
- Date picker prevents future date selection
- All frontend tests pass (vitest: 20 tests)
- UI is fully responsive on mobile and desktop
- `run_audit.ps1` passes all checks

---

## Phase 4 — Data Import & Export

**Objective:** Enable bulk transaction import from CSV and export to CSV/Excel. Critical for migrating from other tools and backup.

**Deliverables:**
- Backend: CSV parser service with validation
  - Parse CSV with columns: date, amount, type, category_name, description
  - Validate each row (date format, amount positive, type valid)
  - Match category by name (case-insensitive)
  - Create missing categories automatically (optional flag)
  - Return detailed import results (success count, error list with row numbers)
- Backend: Export service
  - Generate CSV from transaction query results
  - Include all transaction fields plus category name
  - Apply same filters as transaction list
  - Return as downloadable file with proper headers
- API routes:
  - `POST /transactions/import` — upload CSV file, return import results
  - `GET /transactions/export` — download CSV with optional filters
  - `GET /transactions/export?format=xlsx` — download Excel file
- CSV template generation: `GET /transactions/template` — download empty CSV with proper headers
- Frontend components:
  - `ImportModal` — drag-and-drop file upload with preview
  - `ImportResults` — display success/error summary after import
  - `ExportButton` — dropdown with CSV/Excel options
- File upload handling with size limit (5MB)
- Progress indicator during import processing
- Excel export using openpyxl (formatted with headers and auto-column width)
- Unit tests for CSV parser (10 tests covering various edge cases)
- Unit tests for export service (5 tests)
- Integration tests for import/export endpoints (8 tests)
- Frontend tests for import/export components (6 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- Can import valid CSV with 100+ transactions
- Import validation catches and reports all errors with row numbers
- Can optionally auto-create missing categories during import
- Export generates valid CSV that can be re-imported
- Export respects active filters
- Excel export opens correctly in Microsoft Excel and Google Sheets
- Template download provides correct CSV structure
- All tests pass (pytest: 23 tests, vitest: 6 tests)
- Import handles large files (1000+ rows) without timeout
- `run_audit.ps1` passes all checks

---

## Phase 5 — Analytics & Insights

**Objective:** Provide visual insights into financial trends. Help users understand spending patterns and income sources.

**Deliverables:**
- Backend analytics service:
  - Calculate monthly income/expense breakdown
  - Calculate category distribution (top spending categories)
  - Calculate trend data (month-over-month change)
  - Calculate running balance over time
- API routes:
  - `GET /analytics/monthly` — monthly income/expense totals for past 12 months
  - `GET /analytics/categories` — breakdown by category with percentages
  - `GET /analytics/trends` — month-over-month growth rates
  - `GET /analytics/balance-history` — running balance data points
- Frontend charting library integration (Chart.js or Recharts)
- Frontend components:
  - `MonthlyChart` — bar chart showing income vs expenses by month
  - `CategoryPieChart` — pie chart showing expense distribution by category
  - `BalanceLineChart` — line chart showing balance over time
  - `TrendIndicators` — up/down arrows with percentage change
  - `InsightsPanel` — highlight key metrics (highest expense category, average monthly income, etc.)
- Frontend pages:
  - `AnalyticsPage` — dashboard with all charts and insights
- Chart interactivity:
  - Tooltips showing exact values
  - Clickable segments to filter transactions
  - Responsive charts that reflow on mobile
- Date range selector for analytics (last 30/90/365 days, custom range)
- Export charts as images (PNG)
- Unit tests for analytics service (12 tests)
- Integration tests for analytics endpoints (6 tests)
- Frontend component tests for charts (8 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)

**Exit criteria:**
- Monthly chart displays correct income/expense totals
- Category pie chart shows accurate distribution
- Balance line chart reflects running total correctly
- All charts are responsive and work on mobile
- Charts update when date range changes
- Trend indicators show correct month-over-month change
- All tests pass (pytest: 18 tests, vitest: 8 tests)
- Analytics endpoints return data in under 500ms for 1000+ transactions
- `run_audit.ps1` passes all checks

---

## Phase 6 — Performance & Polish

**Objective:** Optimize query performance, add database indexes, implement caching, and polish UX details.

**Deliverables:**
- Database performance optimization:
  - Add composite index on `transactions(date, type)` for filtered queries
  - Add index on `transactions(created_at)` for recent activity queries
  - Implement database query analysis and explain plans
  - Add connection pooling configuration tuning
- Backend caching layer:
  - Cache category list (rarely changes)
  - Cache transaction summary (invalidate on transaction change)
  - Use Redis or in-memory cache
- API response optimization:
  - Implement field selection (`?fields=id,amount,date` to reduce payload)
  - Add compression middleware (gzip)
  - Implement ETag support for conditional requests
- Frontend performance:
  - Implement virtual scrolling for large transaction lists (react-window)
  - Add debounced search/filter inputs
  - Lazy load charts and analytics page
  - Optimize re-renders with React.memo and useMemo
  - Implement optimistic updates for better perceived performance
- UX polish:
  - Add keyboard shortcuts (N for new transaction, / for search, etc.)
  - Add toast notifications for all actions
  - Add confirmation dialogs for destructive actions
  - Add undo functionality for delete operations (5-second window)
  - Improve loading states with skeleton screens
  - Add error boundary for graceful error handling
  - Add accessibility improvements (ARIA labels, keyboard navigation)
- Frontend error handling:
  - Retry logic for failed API calls
  - Offline detection and messaging
  - Form auto-save to localStorage
- Performance monitoring:
  - Add API response time logging
  - Add frontend performance metrics (Core Web Vitals)
- Load testing with 10,000 transactions
- Performance benchmark tests (6 tests)
- Accessibility audit and fixes
- Cross-browser testing checklist

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)
- Additional indexes added

**Exit criteria:**
- Transaction list renders 1000+ items smoothly with virtual scrolling
- API response times under 100ms for cached data
- Category dropdown responds instantly (cached)
- All filter operations complete in under 200ms
- Page load time under 2 seconds on 3G connection
- Lighthouse score above 90 for Performance, Accessibility, Best Practices
- Keyboard shortcuts work correctly
- Undo delete restores transaction correctly
- All tests pass including performance benchmarks
- `run_audit.ps1` passes all checks

---

## Phase 7 — Search & Advanced Filters

**Objective:** Implement full-text search across transactions and advanced filtering capabilities for power users.

**Deliverables:**
- Database: Add full-text search index on `transactions.description`
- Backend search service:
  - Full-text search on description field
  - Search across multiple fields (description, category name, amount range)
  - Fuzzy matching for typo tolerance
  - Search result ranking and relevance scoring
- API routes:
  - `GET /transactions/search?q={query}` — full-text search
  - `GET /transactions/search?q={query}&type=expense` — search with filters
  - `GET /transactions?amount_min=100&amount_max=500` — amount range filter
  - `GET /transactions?sort=amount&order=desc` — sorting options
- Advanced filter combinations:
  - Multiple categories (OR logic)
  - Exclude categories (NOT logic)
  - Amount ranges (min/max)
  - Custom date ranges with presets (This Month, Last Quarter, etc.)
- Frontend components:
  - `SearchBar` — autocomplete search with recent searches
  - `AdvancedFilters` — expandable panel with all filter options
  - `FilterChips` — active filters displayed as removable chips
  - `SavedFilters` — save and reuse filter combinations
- Search features:
  - Highlight matching text in results
  - Search suggestions based on common queries
  - Recent searches history (localStorage)
  - Clear all filters button
- Query builder for complex filter combinations
- Search performance optimization (debounced input, cached results)
- Unit tests for search service (10 tests)
- Integration tests for search endpoints (8 tests)
- Frontend tests for search and filter components (10 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)
- Full-text search index added

**Exit criteria:**
- Search returns relevant results within 200ms
- Fuzzy search handles common typos
- Advanced filters can be combined (e.g., expense + category + amount range)
- Saved filters persist across sessions
- Search highlights matching terms in results
- All filter combinations work correctly together
- All tests pass (pytest: 18 tests, vitest: 10 tests)
- Search handles 10,000+ transactions efficiently
- `run_audit.ps1` passes all checks

---

## Phase 8 — Recurring Transactions

**Objective:** Support recurring income and expenses with automatic generation. Essential for predictable cash flow management.

**Deliverables:**
- Database migration: `recurring_transactions` table (id UUID PRIMARY KEY, amount DECIMAL(10,2) NOT NULL, type VARCHAR(10) NOT NULL, category_id UUID FK, description TEXT, frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')), start_date DATE NOT NULL, end_date DATE, last_generated TIMESTAMP, is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW())
- Repository layer: `RecurringTransactionRepository` with CRUD methods
- Service layer: `RecurringTransactionService` with business logic:
  - Create recurring transaction template
  - Generate actual transactions based on schedule
  - Handle end dates and automatic deactivation
  - Preview upcoming transactions (next 3 months)
- Scheduled task service:
  - Daily job to generate due recurring transactions
  - Background task runner (APScheduler or Celery)
  - Job logging and error handling
- API routes:
  - `POST /recurring-transactions` — create recurring template
  - `GET /recurring-transactions` — list all recurring templates
  - `GET /recurring-transactions/{id}` — get single template
  - `PUT /recurring-transactions/{id}` — update template
  - `DELETE /recurring-transactions/{id}` — delete template
  - `POST /recurring-transactions/{id}/pause` — pause generation
  - `POST /recurring-transactions/{id}/resume` — resume generation
  - `GET /recurring-transactions/{id}/preview` — preview next 5 occurrences
- Pydantic models: `RecurringTransactionCreate`, `RecurringTransactionUpdate`, `RecurringTransactionResponse`, `RecurringPreview`
- Frontend components:
  - `RecurringList` — list of all recurring templates with status badges
  - `RecurringForm` — form with frequency selector and date range
  - `RecurringPreview` — modal showing upcoming transactions
  - `RecurringBadge` — indicator on transaction list showing auto-generated items
- Frequency options: Daily, Weekly (every 7 days), Bi-weekly (every 14 days), Monthly (same day each month), Yearly
- Smart date handling for month-end edge cases (e.g., monthly on 31st)
- Notification system for failed recurring generation
- Unit tests for recurring service (15 tests covering all frequencies and edge cases)
- Integration tests for recurring endpoints (12 tests)
- Frontend tests for recurring components (8 tests)
- Scheduled task tests (5 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)
- [x] `recurring_transactions` table

**Exit criteria:**
- Can create recurring transaction with all frequency types
- Daily job generates transactions correctly
- Monthly recurring handles month-end dates properly (e.g., Jan 31 → Feb 28)
- Can pause and resume recurring templates
- Preview shows correct upcoming dates
- Auto-generated transactions appear in main transaction list with badge
- End date stops generation automatically
- All tests pass (pytest: 32 tests, vitest: 8 tests)
- Scheduled job runs reliably without failures
- `run_audit.ps1` passes all checks

---

## Phase 9 — Budget Tracking

**Objective:** Set and monitor category budgets with alerts when approaching or exceeding limits.

**Deliverables:**
- Database migration: `budgets` table (id UUID PRIMARY KEY, category_id UUID FK, amount DECIMAL(10,2) NOT NULL, period VARCHAR(20) NOT NULL CHECK (period IN ('weekly', 'monthly', 'quarterly', 'yearly')), start_date DATE NOT NULL, is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW())
- Repository layer: `BudgetRepository` with CRUD methods
- Service layer: `BudgetService` with business logic:
  - Calculate budget vs actual spending
  - Calculate remaining budget
  - Calculate percentage used
  - Trigger alerts when thresholds crossed (50%, 80%, 100%, 120%)
  - Handle budget rollover for new periods
- API routes:
  - `POST /budgets` — create budget for category
  - `GET /budgets` — list all active budgets
  - `GET /budgets/{id}` — get single budget with current status
  - `PUT /budgets/{id}` — update budget amount or period
  - `DELETE /budgets/{id}` — delete budget
  - `GET /budgets/status` — overall budget health summary
  - `GET /budgets/{id}/history` — historical budget performance
- Budget status calculation:
  - Under budget (green)
  - At risk (yellow, 80%+)
  - Over budget (red, 100%+)
  - Severely over budget (dark red, 120%+)
- Alert system:
  - Generate alert when threshold crossed
  - Store alerts in database for history
  - Display alerts on dashboard
- Frontend components:
  - `BudgetList` — list of budgets with progress bars
  - `BudgetForm` — form to create/edit budget with period selector
  - `BudgetProgress` — visual progress bar with percentage and remaining amount
  - `BudgetAlerts` — notification banner for budget warnings
  - `BudgetCard` — individual budget display with status indicator
- Frontend pages:
  - `BudgetsPage` — budget management dashboard
- Dashboard integration:
  - Add budget summary to main dashboard
  - Show budget alerts prominently
  - Quick link to over-budget categories
- Period handling for all budget types (week starts Monday, month starts 1st, etc.)
- Budget rollover automation (reset counters for new period)
- Historical budget tracking (compare actual vs budget over time)
- Unit tests for budget service (18 tests covering calculations and alerts)
- Integration tests for budget endpoints (10 tests)
- Frontend tests for budget components (10 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)
- [x] `recurring_transactions` table (Phase 8)
- [x] `budgets` table

**Exit criteria:**
- Can create budget for any expense category
- Budget vs actual calculates correctly for all period types
- Alerts trigger at correct thresholds (50%, 80%, 100%, 120%)
- Progress bars reflect accurate percentage
- Budget status updates in real-time as transactions are added
- Monthly budgets roll over correctly on the 1st
- Historical view shows past budget performance
- Cannot create budget for income categories (expense only)
- All tests pass (pytest: 28 tests, vitest: 10 tests)
- `run_audit.ps1` passes all checks

---

## Phase 10 — Multi-Currency Support

**Objective:** Support multiple currencies with real-time exchange rates and currency conversion.

**Deliverables:**
- Database migration: Add `currency` VARCHAR(3) DEFAULT 'USD' to `transactions` table
- Database migration: `exchange_rates` table (id UUID PRIMARY KEY, from_currency VARCHAR(3), to_currency VARCHAR(3), rate DECIMAL(10,6), fetched_at TIMESTAMP)
- Database migration: `user_settings` table (id UUID PRIMARY KEY, default_currency VARCHAR(3) DEFAULT 'USD', display_currency VARCHAR(3) DEFAULT 'USD')
- External API integration: Exchange rate provider (e.g., exchangerate-api.io)
- Backend service: `CurrencyService` with methods:
  - Fetch latest exchange rates
  - Convert amount between currencies
  - Cache rates (update daily)
  - Handle rate fetch failures gracefully
- Repository layer: `ExchangeRateRepository` and `UserSettingsRepository`
- API routes:
  - `GET /currencies` — list supported currencies
  - `GET /exchange-rates` — current rates for all supported currencies
  - `POST /exchange-rates/convert` — convert amount between two currencies
  - `GET /settings/currency` — get user currency preferences
  - `PUT /settings/currency` — update default and display currencies
- Currency list: Support major currencies (USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR)
- Transaction updates:
  - Store original currency with each transaction
  - Display amounts in user's preferred display currency
  - Show original currency in tooltips
- Summary calculations:
  - Convert all transactions to display currency for totals
  - Show multi-currency breakdown (amounts in original currencies)
- Frontend components:
  - `CurrencySelector` — dropdown with currency codes and symbols
  - `CurrencyDisplay` — format amount with proper symbol and decimal places
  - `CurrencyConverter` — quick conversion tool
  - `MultiCurrencyWarning` — alert when viewing mixed-currency data
- Transaction form: Currency selector with default from user settings
- Settings page: Currency preference management
- Exchange rate caching (24-hour TTL)
- Scheduled task to refresh exchange rates daily
- Fallback to cached rates if API unavailable
- Unit tests for currency service (15 tests including conversion accuracy)
- Integration tests for currency endpoints (8 tests)
- Frontend tests for currency components (8 tests)

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2) — updated with currency field
- [x] `recurring_transactions` table (Phase 8)
- [x] `budgets` table (Phase 9)
- [x] `exchange_rates` table
- [x] `user_settings` table

**Exit criteria:**
- Can create transactions in any supported currency
- Exchange rates fetch successfully from API
- Conversion between currencies is accurate (within 0.01%)
- Summary totals reflect converted amounts correctly
- Display currency setting persists across sessions
- Exchange rates cache for 24 hours
- Fallback to cached rates works when API unavailable
- Currency symbols display correctly (€, £, ¥, etc.)
- All tests pass (pytest: 23 tests, vitest: 8 tests)
- `run_audit.ps1` passes all checks

---

## Phase 11 — Ship & Deploy

**Objective:** Production hardening, comprehensive documentation, deployment configuration, and final quality assurance.

**Deliverables:**
- Environment configuration:
  - Production `.env.example` with all required variables documented
  - Environment validation on startup (fail fast if missing critical vars)
  - Secret management guidelines (database URL, API keys)
- Deployment configuration:
  - Render deployment configuration (`render.yaml`)
  - Database migration strategy for Render (auto-migrate on deploy)
  - Static file serving configuration
  - CORS configuration for production domain
- Security hardening:
  - Input validation on all API endpoints (Pydantic strict mode)
  - SQL injection prevention audit (parameterized queries)
  - Rate limiting on all endpoints (100 req/min per IP)
  - HTTPS enforcement
  - Security headers (HSTS, CSP, X-Frame-Options)
  - Dependency vulnerability scan
- Error handling:
  - Global exception handler (no stack traces leak to client)
  - Structured error responses with error codes
  - Error logging to file and console
  - Sentry integration for error tracking (optional)
- Performance optimization:
  - Database connection pool tuning for Render
  - Static asset caching headers
  - Database query optimization review
  - Load testing with 1000 concurrent users
- Logging:
  - Structured logging (JSON format)
  - Log levels configured by environment
  - Request/response logging with sanitization
  - Database query logging in development only
- Monitoring:
  - Health check endpoint enhanced with DB connection status
  - `/metrics` endpoint for basic metrics (request count, errors, response times)
  - Database connection pool metrics
- Documentation:
  - **README.md** — comprehensive project documentation including:
    - Project description and purpose
    - Key features list
    - Tech stack overview
    - Prerequisites (Python 3.11+, Node 18+, PostgreSQL)
    - Local setup instructions (clone, install, configure, run)
    - Environment variables reference (all vars documented)
    - Database setup and migration instructions
    - API documentation (all endpoints with examples)
    - Frontend build and deployment
    - Troubleshooting guide (common issues and solutions)
    - Contributing guidelines
    - License information
  - `DEPLOYMENT.md` — Render deployment guide with step-by-step instructions
  - `API.md` — complete API reference with request/response examples
  - `ARCHITECTURE.md` — system architecture and design decisions
  - Inline code documentation (docstrings for all public methods)
- Testing:
  - Full test suite run (all tests must pass)
  - E2E tests with Playwright covering critical user journeys:
    - Create transaction flow
    - Filter and search flow
    - Budget creation and alert flow
    - Import/export flow
  - Cross-browser testing (Chrome, Firefox, Safari)
  - Mobile responsive testing (iOS Safari, Chrome Android)
- Quality assurance:
  - Code coverage above 80% (pytest-cov)
  - Linting passes (Black, isort, ESLint, Prettier)
  - Type checking passes (mypy for Python, tsc for TypeScript)
  - No console errors or warnings
  - Accessibility audit with axe DevTools
- Deployment scripts:
  - `boot.ps1` — complete local setup automation (one command to full stack)
  - `deploy.ps1` — deployment validation and pre-deploy checks
  - `run_audit.ps1` — comprehensive audit including all quality checks
- Production smoke tests:
  - Automated test suite that runs against deployed app
  - Verify all critical endpoints return expected responses
  - Verify database migrations applied correctly

**Schema coverage:**
- [x] `categories` table (Phase 1)
- [x] `transactions` table (Phase 2)
- [x] `recurring_transactions` table (Phase 8)
- [x] `budgets` table (Phase 9)
- [x] `exchange_rates` table (Phase 10)
- [x] `user_settings` table (Phase 10)

**Exit criteria:**
- `boot.ps1` brings up full stack from fresh clone in under 5 minutes
- All tests pass (pytest: 200+ tests, vitest: 80+ tests, E2E: 20+ tests)
- Code coverage above 80%
- No linting errors or type errors
- README.md is comprehensive and accurate
- API documentation matches actual implementation
- Application deploys successfully to Render
- Production smoke tests pass
- No console errors in browser
- Lighthouse scores: Performance 90+, Accessibility 95+, Best Practices 95+, SEO 90+
- Load test handles 1000 concurrent users without errors
- All environment variables documented
- Security headers configured correctly
- Rate limiting works (returns 429 when exceeded)
- `run_audit.ps1` passes all checks
- Application is publicly accessible and functional on Render URL