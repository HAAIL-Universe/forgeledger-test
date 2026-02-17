# ForgeLedger Test — Technology Stack

Canonical technology decisions for this project. The builder contract (S1) requires reading this file before making changes. All implementation must use the technologies declared here unless a directive explicitly approves a change.

---

## Backend

- **Language:** Python 3.11+
- **Framework:** FastAPI 0.104+
- **Package manager:** pip
- **Dependency file:** requirements.txt
- **Virtual environment:** venv (`.venv/`)
- **ASGI server:** uvicorn

**Rationale:** FastAPI chosen for its automatic OpenAPI documentation generation, built-in request validation via Pydantic, excellent async support for database operations, and type-safe development experience. Python selected for rapid development, strong ecosystem for financial applications, and alignment with questionnaire requirements.

**Key libraries:**
- `fastapi` — Web framework
- `uvicorn[standard]` — ASGI server with performance optimizations
- `pydantic` — Data validation and settings management
- `asyncpg` — PostgreSQL async driver
- `python-dateutil` — Date manipulation for transaction filtering
- `python-dotenv` — Environment variable management

---

## Database

- **Engine:** PostgreSQL 15+
- **Host:** Neon (serverless PostgreSQL)
- **Driver/client:** asyncpg
- **ORM strategy:** Repository pattern with raw SQL (no ORM)
- **Schema management:** SQL migration files in `db/migrations/`
- **Connection pooling:** asyncpg connection pool

**Rationale:** PostgreSQL chosen for ACID compliance critical to financial data integrity, excellent DECIMAL type support for precise monetary calculations, and robust transaction handling. Neon provides serverless PostgreSQL with automatic scaling and connection pooling. Raw SQL via repository pattern selected over ORM for explicit control over financial queries, better performance visibility, and simpler debugging of monetary calculations.

**Schema conventions:**
- UUID primary keys for all tables (collision-resistant, non-sequential)
- DECIMAL(10,2) for monetary amounts (no floating-point precision issues)
- Timestamps with timezone awareness (UTC storage)
- Foreign key constraints enforced at database level
- CHECK constraints for transaction/category types

---

## Auth

- **Strategy:** None (unauthenticated application)
- **Authorization:** Not implemented
- **Session management:** N/A

**Rationale:** Per questionnaire specification, this is a simple application without authentication requirements. All endpoints are publicly accessible. Future enhancement to add user authentication would require revisiting this contract.

---

## Frontend

- **Enabled:** Yes
- **Language:** TypeScript 5.0+
- **Framework:** React 18+
- **Build tool:** Vite 5+
- **Package manager:** npm
- **Directory:** `web/`
- **Style approach:** CSS Modules + modern CSS (Grid/Flexbox)

**Rationale:** React selected for component reusability and mature ecosystem. TypeScript provides type safety crucial for financial data handling and reduces runtime errors. Vite chosen for fast dev server, optimized production builds, and excellent TypeScript/React developer experience. CSS Modules prevent style conflicts while maintaining simple, functional design per requirements.

**Key libraries:**
- `react` — UI framework
- `react-dom` — React rendering
- `react-router-dom` — Client-side routing
- `date-fns` — Date formatting and manipulation
- `axios` — HTTP client for API communication
- `@tanstack/react-query` — Server state management and caching

**Component architecture:**
- Presentation components (pure UI)
- Container components (data fetching)
- Custom hooks for business logic
- Shared utilities for formatting (currency, dates)

---

## LLM / AI Integration

- **Enabled:** No
- **Provider:** N/A
- **Integration point:** N/A
- **Embedding / vector search:** N/A

**Rationale:** Not required for MVP financial ledger functionality.

---

## Testing

### Backend Testing
- **Framework:** pytest 7.4+
- **Coverage target:** 80% minimum
- **Test directory:** `tests/`
- **Test types:**
  - Unit tests for business logic (repositories, services)
  - Integration tests for API endpoints
  - Database tests against test database

**Key testing libraries:**
- `pytest` — Test framework
- `pytest-asyncio` — Async test support
- `pytest-cov` — Coverage reporting
- `httpx` — Async HTTP client for endpoint testing

### Frontend Testing
- **Framework:** Vitest 1.0+
- **Component testing:** React Testing Library
- **Coverage target:** 70% minimum
- **Test directory:** `web/src/__tests__/`
- **E2E testing:** Not in MVP scope

**Key testing libraries:**
- `vitest` — Test runner (Vite-native)
- `@testing-library/react` — Component testing utilities
- `@testing-library/user-event` — User interaction simulation
- `@vitest/ui` — Test UI dashboard

**Rationale:** pytest selected for excellent async support and fixture system ideal for database testing. Vitest chosen for seamless Vite integration and faster execution than Jest. 80% backend coverage enforced due to financial data sensitivity; 70% frontend acceptable given UI-heavy nature.

---

## Deployment

- **Target platform:** Render (Web Service)
- **Database host:** Neon (managed PostgreSQL)
- **Backend deployment:** Native Python (no containerization)
- **Frontend deployment:** Static site build served by backend
- **Server process:** uvicorn
- **Environment:** Development/local primary; production-ready configuration available

**Rationale:** Render selected per questionnaire requirements, provides free tier for development, automatic HTTPS, and simple Python deployment without Docker complexity. Neon provides serverless PostgreSQL with generous free tier and automatic connection pooling. Frontend built as static assets and served by FastAPI's StaticFiles middleware, simplifying deployment to single service.

**Deployment configuration:**
- Build command: `pip install -r requirements.txt && cd web && npm install && npm run build`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check endpoint: `/health`
- Static files served from: `web/dist/`

**Expected scale:**
- Concurrent users: <100
- Transactions per day: <1000
- Database size: <1GB
- Response time target: <500ms (p95)

---

## Environment Variables

### Required Variables

| Variable | Purpose | Example | Validation |
|----------|---------|---------|------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) | `postgresql://user:pass@ep-xxx.neon.tech/forgeledger?sslmode=require` | Must start with `postgresql://` |
| `ENVIRONMENT` | Deployment environment | `development`, `production` | Enum validation |

### Optional Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173` | `http://localhost:5173,https://app.forgeledger.com` |
| `LOG_LEVEL` | Application logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DB_POOL_MIN_SIZE` | Minimum database connection pool size | `2` | `2` |
| `DB_POOL_MAX_SIZE` | Maximum database connection pool size | `10` | `10` |
| `API_PREFIX` | API route prefix | `/api` | `/api/v1` |

### Development-Only Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `RELOAD` | Enable auto-reload (uvicorn) | `true` | `true`, `false` |
| `DEBUG` | Enable debug mode | `true` | `true`, `false` |

**Security notes:**
- Never commit `.env` file to version control
- Use `.env.example` as template
- Rotate `DATABASE_URL` credentials if exposed
- Neon credentials include SSL mode requirement

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
    "version": "3.11+",
    "framework": "fastapi",
    "entry_module": "app.main",
    "entry_point": "app",
    "test_framework": "pytest",
    "test_dir": "tests",
    "test_command": "pytest tests/ -v --cov=app --cov-report=term-missing",
    "dependency_file": "requirements.txt",
    "venv_path": ".venv",
    "python_path": "PYTHONPATH=.",
    "dev_server": {
      "command": "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
      "port": 8000
    }
  },
  "database": {
    "engine": "postgresql",
    "version": "15+",
    "host": "neon",
    "driver": "asyncpg",
    "migrations_dir": "db/migrations",
    "schema_file": "db/schema.sql",
    "seed_file": "db/seed.sql"
  },
  "frontend": {
    "enabled": true,
    "language": "typescript",
    "framework": "react",
    "build_tool": "vite",
    "dir": "web",
    "entry_point": "src/main.tsx",
    "build_cmd": "npm run build",
    "dev_cmd": "npm run dev",
    "test_cmd": "npm run test",
    "test_framework": "vitest",
    "dist_dir": "dist",
    "dev_server": {
      "port": 5173
    }
  },
  "api": {
    "style": "REST",
    "prefix": "/api",
    "documentation": "/docs",
    "version": "v1"
  },
  "deployment": {
    "platform": "render",
    "type": "web_service",
    "region": "oregon",
    "plan": "free",
    "health_check_path": "/health",
    "build_command": "pip install -r requirements.txt && cd web && npm install && npm run build",
    "start_command": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  },
  "features": {
    "authentication": false,
    "authorization": false,
    "websockets": false,
    "background_jobs": false,
    "file_uploads": false,
    "email": false
  },
  "code_quality": {
    "backend_linter": "ruff",
    "backend_formatter": "black",
    "frontend_linter": "eslint",
    "frontend_formatter": "prettier",
    "type_checker": "mypy"
  }
}
```

---

## Additional Technical Decisions

### API Design Conventions
- RESTful resource-based URLs
- JSON request/response bodies
- HTTP status codes: 200 (success), 201 (created), 400 (validation error), 404 (not found), 500 (server error)
- Error responses include `detail` field with human-readable message
- List endpoints support query parameters: `type`, `category_id`, `start_date`, `end_date`
- ISO 8601 date format for all date fields
- Monetary amounts always returned as strings to preserve precision

### Backend Project Structure
```
app/
├── main.py              # FastAPI application factory
├── config.py            # Settings and configuration
├── models/              # Pydantic models (request/response schemas)
├── repositories/        # Database access layer
├── services/            # Business logic layer
├── routers/             # API route handlers
└── utils/               # Shared utilities (date formatting, validation)

db/
├── migrations/          # SQL migration files (numbered)
└── schema.sql           # Initial schema definition

tests/
├── conftest.py          # Pytest fixtures
├── test_repositories/   # Repository tests
├── test_services/       # Service layer tests
└── test_api/            # API endpoint tests
```

### Frontend Project Structure
```
web/
├── src/
│   ├── main.tsx              # Application entry point
│   ├── App.tsx               # Root component
│   ├── components/           # Reusable UI components
│   │   ├── TransactionList/
│   │   ├── TransactionForm/
│   │   ├── CategoryManager/
│   │   └── FilterBar/
│   ├── pages/                # Page-level components
│   │   └── Dashboard/
│   ├── services/             # API client services
│   │   ├── api.ts
│   │   ├── transactions.ts
│   │   └── categories.ts
│   ├── hooks/                # Custom React hooks
│   ├── utils/                # Utility functions (formatting, validation)
│   ├── types/                # TypeScript type definitions
│   └── __tests__/            # Frontend tests
├── public/                   # Static assets
├── index.html                # HTML entry point
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # NPM dependencies
```

### Code Quality Standards
- **Backend:** Black formatting (line length 100), Ruff linting, mypy type checking (strict mode)
- **Frontend:** Prettier formatting, ESLint with TypeScript rules, strict TypeScript configuration
- **Documentation:** Docstrings for all public functions, JSDoc for exported TypeScript functions
- **Git hooks:** Pre-commit hooks for formatting and linting (optional but recommended)

### Database Migration Strategy
- Sequential numbered migrations: `001_initial_schema.sql`, `002_add_index.sql`
- Each migration must be idempotent (safe to run multiple times)
- Rollback script for each migration (optional but recommended)
- Migration tracking table: `schema_migrations` with version and applied timestamp

### Error Handling Strategy
- **Backend:** Structured exceptions with specific error types (ValidationError, NotFoundError, DatabaseError)
- **Frontend:** Centralized error handling with user-friendly messages
- **Logging:** Structured logging with correlation IDs for request tracing
- **Database errors:** Catch and translate constraint violations to user-friendly messages