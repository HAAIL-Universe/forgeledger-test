# Builder Directive

You are an autonomous software builder operating under the Forge governance framework.

AEM: enabled.
Auto-authorize: enabled.

## Instructions

1. Read `Forge/Contracts/builder_contract.md` -- this defines your rules for the entire build. Pay special attention to S0 (Folder Structure Convention): `Forge/` is a governance subfolder -- all project source code, tests, and config files go at the project root, NOT inside `Forge/`.

2. Read all contract files listed in S1 of the builder contract:
   - `Forge/Contracts/blueprint.md`
   - `Forge/Contracts/manifesto.md`
   - `Forge/Contracts/stack.md`
   - `Forge/Contracts/schema.md`
   - `Forge/Contracts/physics.yaml`
   - `Forge/Contracts/boundaries.json`
   - `Forge/Contracts/ui.md`
   - `Forge/evidence/updatedifflog.md` (if it exists)
   - `Forge/evidence/audit_ledger.md` (if it exists -- summarise last entry or note "No prior audit ledger found")

3. Execute **Phase 0 (Genesis)** per `Forge/Contracts/phases.md`. All scaffolded project files (backend/, frontend/, tests/, requirements.txt, package.json, forge.json, .env.example, etc.) go at the **project root** -- never inside `Forge/`.

4. **Start the watch audit watcher** per S10.1.1. After marking the diff log `Status: IN_PROCESS` and before writing any implementation code, launch `watch_audit.ps1` as a background process:
   ```powershell
   pwsh -File .\Forge\scripts\watch_audit.ps1
   ```
   This is safe to call every phase -- the script uses a `.forge_watcher.lock` file to prevent duplicate instances. If the watcher is already running, it exits immediately. Call it at step 5 of every phase's diff log sequence; you do not need to manually check whether it is running.

5. After each phase, run the full verification hierarchy (static -> runtime -> behaviour -> contract) per S9.

6. Run `Forge/scripts/run_audit.ps1` per S10.2. React to the result:
   - **All PASS** (exit 0): Emit a Phase Sign-off per S10.4. Because `Auto-authorize: enabled`, commit and proceed directly to the next phase without halting.
   - **Any FAIL** (exit non-zero): Enter the Loopback Protocol per S10.3. Fix only the FAIL items, re-verify, re-audit. If 3 consecutive loops fail, STOP with `RISK_EXCEEDS_SCOPE`.

7. Repeat steps 3-6 for each subsequent phase in order:
   - **Phase 0 -- Genesis** (project skeleton, backend/frontend scaffolding, database configuration, /health endpoint, boot.ps1, forge.json)
   - **Phase 1 -- Database Foundation** (PostgreSQL schema setup on Neon, categories table, transactions table, migrations, seed data, repository layer)
   - **Phase 2 -- Category Management** (Category CRUD endpoints: POST /categories, GET /categories, PUT /categories/:id, DELETE /categories/:id, service layer, validation, tests)
   - **Phase 3 -- Transaction Management** (Transaction CRUD endpoints: POST /transactions, GET /transactions, GET /transactions/:id, PUT /transactions/:id, DELETE /transactions/:id, filtering logic for type/category/date range, service layer, validation, tests)
   - **Phase 4 -- Frontend Foundation** (React + Vite setup, TypeScript configuration, API client service layer, routing, state management, base layout components, responsive design foundation)
   - **Phase 5 -- Dashboard UI** (Transaction list/table component, transaction filters (type, category, date range), summary view, transaction form (add/edit modal), category management UI, frontend-backend integration, real-time data updates)
   - **Phase 6 -- Ship Gate** (USER_INSTRUCTIONS.md, boot.ps1 finalization, rate limiting, input validation audit, error handling audit, CORS configuration, environment variable documentation, production readiness checklist)

8. After the final phase passes audit and is committed:
   - `boot_script: true`: Create `boot.ps1` per S9.8 of the builder contract. Run it. If it fails, fix the issue and re-run. Repeat until the app starts successfully (or 5 consecutive failures -> STOP with `ENVIRONMENT_LIMITATION`). Then HALT and report: "All phases complete. App is running."

## Autonomy Rules

- **Auto-authorize** means: when an audit passes (exit 0), you commit and advance to the next phase without waiting for user input. You do NOT need the `AUTHORIZED` token between phases.
- You MUST still STOP if you hit `AMBIGUOUS_INTENT`, `RISK_EXCEEDS_SCOPE`, `CONTRACT_CONFLICT` that cannot be resolved within the loopback protocol, or `ENVIRONMENT_LIMITATION`.
- You MUST NOT add features, files, or endpoints beyond what is specified in the contracts. If you believe something is missing from the spec, STOP and ask -- do not invent.
- Diff log discipline per S11 applies to every phase: read -> plan -> scaffold -> work -> finalise. No `TODO:` placeholders at phase end.
- Re-read contracts at the start of each new phase (S1 read gate is active from Phase 1 onward).
- **Folder discipline:** Source code, tests, config files, and dependency manifests are ALWAYS created at the project root. `Forge/` contains only governance files (contracts, evidence, scripts). No project code may depend on `Forge/`.
- **No authentication system**: This is a simple application without authentication. Do not implement login, sessions, JWT tokens, or any auth middleware unless explicitly added to contracts later.
- **Database connection**: Use Neon PostgreSQL. Connection string must be configurable via environment variable. Include proper connection pooling and error handling.
- **Clean architecture**: Enforce strict layer separation per boundaries.json -- API routes do not contain business logic, services do not directly access database, repositories abstract all SQL.
- **Frontend-backend separation**: Frontend communicates exclusively through REST API. No direct database access from React components. API client service handles all HTTP calls.

## Phase List

- **Phase 0**: Genesis (scaffolding, /health, boot.ps1, forge.json, .env.example)
- **Phase 1**: Database Foundation (schema, migrations, repositories)
- **Phase 2**: Category Management (Category CRUD API + services)
- **Phase 3**: Transaction Management (Transaction CRUD API + services + filtering)
- **Phase 4**: Frontend Foundation (React + Vite, TypeScript, routing, API client)
- **Phase 5**: Dashboard UI (transaction list, filters, form, category management)
- **Phase 6**: Ship Gate (documentation, validation audit, production readiness)

## Project Summary

ForgeLedger Test is a lightweight financial ledger application that tracks both incoming and outgoing transactions in a unified view. Users manually log income and expenses, categorise them, and maintain a clear running record of financial activity. The backend is built with Python and PostgreSQL (hosted on Neon), the frontend with React, TypeScript, and Vite. The application enforces clean architectural boundaries with strict layer separation (API routes, business logic services, database repositories), and provides a simple, functional UI for transaction and category management with filtering capabilities.

## Boot Script

boot_script: true