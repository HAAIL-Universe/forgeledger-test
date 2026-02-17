# ForgeLedger Test — Technology Stack

Canonical technology decisions for this project. The builder contract (S1) requires reading this file before making changes. All implementation must use the technologies declared here unless a directive explicitly approves a change.

---

## Backend

- **Language:** Python 3.11+
- **Framework:** FastAPI 0.109+
- **Package manager:** pip
- **Dependency file:** requirements.txt
- **Virtual environment:** .venv/

**Why FastAPI:** Chosen for its modern async capabilities, automatic OpenAPI documentation, excellent type safety with Pydantic, and minimal boilerplate. Perfect for a REST API with clear endpoint contracts. The automatic validation and serialization reduce error-prone manual parsing.

**Key libraries:**
- `pydantic` 2.5+ — Request/response validation and serialization
- `uvicorn` 0.27+ — ASGI server for async FastAPI
- `asyncpg` 0.29+ — High-performance async PostgreSQL driver
- `python-dotenv` 1.0+ — Environment variable management
- `pytest` 7.4+ — Testing framework
- `pytest-asyncio` 0.23+ — Async test support
- `httpx` 0.26+ — HTTP client for testing API endpoints

---

## Database

- **Engine:** PostgreSQL 15+
- **Hosting:** Neon (serverless PostgreSQL)
- **Driver/client:** asyncpg
- **ORM strategy:** Raw SQL via repository pattern (no ORM)
- **Schema management:** SQL migration files in `db/migrations/`
- **Connection pooling:** asyncpg connection pool

**Why PostgreSQL on Neon:** PostgreSQL provides robust ACID guarantees essential for financial data integrity. The DECIMAL type ensures precise monetary calculations without floating-point errors. Neon offers serverless PostgreSQL with automatic scaling, branching for development, and generous free tier — ideal for a financial ledger that needs reliability without operational overhead.

**Why no ORM:** For a simple schema (2 tables) with straightforward queries, raw SQL provides maximum control and performance. The repository pattern maintains clean separation without ORM complexity. Financial applications benefit from explicit query control to ensure correct decimal handling and transaction isolation.

**Migration strategy:**
- Numbered SQL files: `001_initial_schema.sql`, `002_add_index.sql`
- Manual execution via psql or migration runner script
- Forward-only migrations (no automatic rollback)

---

## Auth

- **Strategy:** None (MVP scope)
- **Provider:** N/A
- **Session management:** N/A

**Why no auth:** Project specification explicitly states "authentication: None (simple application)". This is appropriate for a personal financial ledger or internal tool. All API endpoints are publicly accessible. Future auth can be added as a Phase 2 enhancement without architectural changes.

**Security note:** While no user authentication exists, the application should still validate all inputs, use parameterized queries to prevent SQL injection, and enforce business rules at the API layer.

---

## Frontend

- **Enabled:** Yes
- **Language:** TypeScript 5.3+
- **Framework:** React 18.2+
- **Build tool:** Vite 5.0+
- **Directory:** `web/`
- **Package manager:** npm
- **Node version:** 20 LTS

**Why React + TypeScript:** React provides component reusability essential for transaction forms, lists, and filters. TypeScript ensures type safety across API boundaries, catching errors at compile time. The combination is industry-standard with excellent tooling and community support.

**Why Vite:** Vite offers instant hot module replacement, fast cold starts, and optimized production builds. Superior developer experience compared to Create React App. Native ESM support and efficient bundling make it ideal for modern React development.

**Key libraries:**
- `react-router-dom` 6.21+ — Client-side routing for Dashboard and potential future pages
- `@tanstack/react-query` 5.17+ — Server state management, caching, and API data fetching
- `axios` 1.6+ — HTTP client for API communication
- `date-fns` 3.0+ — Date manipulation for transaction date handling
- `react-hook-form` 7.49+ — Form state management for transaction and category forms
- `zod` 3.22+ — Runtime schema validation matching backend Pydantic models

**UI libraries:**
- `@headlessui/react` 1.7+ — Unstyled accessible UI components
- `tailwindcss` 3.4+ — Utility-first CSS framework for rapid UI development

**Why these choices:** React Query eliminates manual cache management and provides automatic refetching, perfect for a live financial ledger. React Hook Form offers performant form handling with minimal re-renders. Zod provides type-safe validation that can be derived from the same schemas used in TypeScript interfaces. Tailwind enables rapid, consistent styling without writing custom CSS.

---

## LLM / AI Integration

- **Enabled:** No
- **Provider:** N/A
- **Integration point:** N/A
- **Embedding / vector search:** N/A

**Rationale:** Not applicable for MVP. Financial ledger requires deterministic, auditable operations. No natural language processing or AI categorization needed for manual transaction entry.

---

## Testing

### Backend Testing
- **Framework:** pytest 7.4+
- **Async support:** pytest-asyncio
- **Coverage tool:** pytest-cov
- **Minimum coverage:** 80% for business logic, 60% overall
- **Test directory:** `tests/`

**Test structure:**
```
tests/
├── unit/           # Business logic and utility tests
├── integration/    # Database repository tests
└── api/            # FastAPI endpoint tests
```

**Why pytest:** Industry standard for Python testing with excellent async support, fixtures, and parameterization. Clear assertion syntax and comprehensive plugin ecosystem.

### Frontend Testing
- **Unit/integration:** Vitest 1.2+
- **Component testing:** React Testing Library 14+
- **Coverage tool:** Vitest coverage (c8)
- **Minimum coverage:** 70% for components, 80% for utility functions
- **Test directory:** `web/src/__tests__/`

**Why Vitest:** Native Vite integration, Jest-compatible API, extremely fast execution. React Testing Library encourages testing user behavior over implementation details, leading to more maintainable tests.

### E2E Testing
- **Framework:** Not included in MVP
- **Future consideration:** Playwright for critical user flows

---

## Deployment

### Platform
- **Target:** Render (Web Service)
- **Server:** uvicorn with Gunicorn worker manager
- **Region:** US-West (or closest to primary users)
- **Instance type:** Starter (512 MB RAM) — sufficient for MVP
- **Containerized:** No (Render native Python deployment)

**Why Render:** Zero-config deployments from Git, free tier for MVP, automatic HTTPS, and managed PostgreSQL integration. Simpler than AWS for a single-service application. Native Python support eliminates Docker complexity while maintaining production-grade hosting.

### Database Hosting
- **Platform:** Neon
- **Connection:** Direct PostgreSQL connection via DATABASE_URL
- **Pooling:** Application-level via asyncpg pool

### Build Process
**Backend:**
1. Render detects Python app via `requirements.txt`
2. Installs dependencies in isolated environment
3. Runs database migrations (via build command)
4. Starts uvicorn server

**Frontend:**
1. Build locally or in separate Render static site
2. Execute `npm run build` → outputs to `web/dist/`
3. Serve via Render static site or backend serves built files

**Build commands (Render):**
- Backend: `pip install -r requirements.txt && python scripts/migrate.py`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Expected Scale (MVP)
- **Users:** 1-10 concurrent users
- **Requests:** <1000 requests/day
- **Database:** <1000 transactions, <50 categories
- **Storage:** <10 MB

---

## Environment Variables

### Required Variables

| Variable | Purpose | Example | Source |
|----------|---------|---------|--------|
| `DATABASE_URL` | PostgreSQL connection string from Neon | `postgresql://user:pass@ep-xxx.neon.tech/forgeledger?sslmode=require` | Neon dashboard |
| `ENVIRONMENT` | Deployment environment identifier | `development`, `production` | Manual config |
| `CORS_ORIGINS` | Allowed frontend origins for CORS | `http://localhost:5173,https://forgeledger.onrender.com` | Manual config |

### Optional Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `LOG_LEVEL` | Application logging verbosity | `INFO` | `DEBUG`, `WARNING`, `ERROR` |
| `DB_POOL_MIN_SIZE` | Minimum database connection pool size | `2` | `5` |
| `DB_POOL_MAX_SIZE` | Maximum database connection pool size | `10` | `20` |
| `API_PREFIX` | API route prefix | `/api/v1` | `/api/v2` |

### Development-Only Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `RELOAD` | Enable uvicorn auto-reload | `true` |
| `DEBUG` | Enable debug mode and detailed errors | `true` |

**Environment file structure:**
- `.env` — Local development (gitignored)
- `.env.example` — Template committed to repo
- Render dashboard — Production variables

---

## forge.json Schema

The builder must create `forge.json` at the project root during Phase 0.

```json
{
  "project_name": "ForgeLedger Test",
  "version": "1.0.0",
  "description": "Lightweight financial ledger for tracking income and expenses",
  "backend": {
    "language": "python",
    "framework": "fastapi",
    "python_version": "3.11",
    "entry_module": "app.main",
    "entry_point": "app",
    "server": "uvicorn",
    "test_framework": "pytest",
    "test_dir": "tests",
    "dependency_file": "requirements.txt",
    "venv_path": ".venv",
    "package_manager": "pip"
  },
  "database": {
    "engine": "postgresql",
    "version": "15",
    "driver": "asyncpg",
    "host": "neon",
    "migration_dir": "db/migrations",
    "orm": "none"
  },
  "frontend": {
    "enabled": true,
    "language": "typescript",
    "framework": "react",
    "build_tool": "vite",
    "dir": "web",
    "package_manager": "npm",
    "node_version": "20",
    "build_cmd": "build",
    "dev_cmd": "dev",
    "test_cmd": "test",
    "output_dir": "dist"
  },
  "deployment": {
    "platform": "render",
    "backend_service_type": "web",
    "frontend_service_type": "static",
    "containerized": false,
    "ci_cd": "none"
  },
  "features": {
    "authentication": false,
    "authorization": false,
    "api_documentation": true,
    "cors": true,
    "rate_limiting": false
  },
  "architecture": {
    "api_style": "REST",
    "backend_pattern": "repository",
    "frontend_pattern": "component_based",
    "state_management": "react_query"
  }
}
```

---

## Code Organization Standards

### Backend Structure
```
app/
├── main.py              # FastAPI app initialization, middleware, CORS
├── config.py            # Environment variables, settings
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── transactions.py   # Transaction endpoints
│   │   └── categories.py     # Category endpoints
│   └── dependencies.py       # Dependency injection (DB pool)
├── services/
│   ├── transaction_service.py  # Business logic for transactions
│   └── category_service.py     # Business logic for categories
├── repositories/
│   ├── transaction_repository.py  # Database access for transactions
│   └── category_repository.py     # Database access for categories
├── models/
│   ├── transaction.py   # Pydantic models for transactions
│   └── category.py      # Pydantic models for categories
└── exceptions.py        # Custom exception classes
```

### Frontend Structure
```
web/
├── src/
│   ├── components/
│   │   ├── transactions/
│   │   │   ├── TransactionList.tsx
│   │   │   ├── TransactionForm.tsx
│   │   │   └── TransactionFilters.tsx
│   │   ├── categories/
│   │   │   ├── CategoryManager.tsx
│   │   │   └── CategoryForm.tsx
│   │   └── ui/             # Reusable UI components
│   ├── services/
│   │   ├── api.ts          # Axios instance, interceptors
│   │   ├── transactions.ts # Transaction API calls
│   │   └── categories.ts   # Category API calls
│   ├── hooks/
│   │   ├── useTransactions.ts  # React Query hooks
│   │   └── useCategories.ts
│   ├── types/
│   │   ├── transaction.ts
│   │   └── category.ts
│   ├── pages/
│   │   └── Dashboard.tsx
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

**Architectural enforcement:**
- API routes only handle HTTP concerns (validation, serialization, status codes)
- Services contain business logic, coordinate between repositories
- Repositories execute SQL queries, return domain objects
- Frontend components don't contain API logic — delegate to services
- React Query manages server state; local state uses React hooks

---

## Development Workflow

### Backend Development
```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
python scripts/migrate.py

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=app
```

### Frontend Development
```bash
# Setup
cd web
npm install

# Start development server
npm run dev  # Runs on http://localhost:5173

# Run tests
npm test

# Build for production
npm run build
```

### Database Management
```bash
# Connect to local PostgreSQL
psql $DATABASE_URL

# Connect to Neon production
psql <neon-connection-string>

# Run specific migration
psql $DATABASE_URL -f db/migrations/001_initial_schema.sql
```

---

## Version Control

### Git Ignore Rules
```
# Python
.venv/
__pycache__/
*.pyc
.pytest_cache/

# Environment
.env
.env.local

# Frontend
web/node_modules/
web/dist/
web/.vite/

# IDE
.vscode/
.idea/
*.swp
```

### Commit Message Convention
```
feat: Add transaction filtering by date range
fix: Correct decimal precision in amount validation
docs: Update API endpoint documentation
test: Add integration tests for category repository
refactor: Extract transaction validation logic to service
```

---

## API Documentation

- **Format:** OpenAPI 3.0 (auto-generated by FastAPI)
- **Access:** `http://localhost:8000/docs` (Swagger UI)
- **Alternative:** `http://localhost:8000/redoc` (ReDoc)
- **Schema endpoint:** `http://localhost:8000/openapi.json`

**Why auto-generated:** FastAPI generates OpenAPI documentation from Pydantic models and route definitions, ensuring documentation stays synchronized with implementation. Reduces maintenance burden and documentation drift.

---

## Performance Targets (MVP)

- API response time: <200ms for list endpoints, <50ms for single resource
- Frontend initial load: <2s on 3G connection
- Time to interactive: <3s
- Database query time: <100ms for filtered transaction queries

**Note:** These are initial targets for a small dataset. Performance optimization is not a Phase 1 priority but should be monitored.