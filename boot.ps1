# boot.ps1 — ForgeLedger Test Bootstrap Script
# Installs backend deps, installs frontend deps, runs DB migrations,
# and starts uvicorn + Vite dev server concurrently.

param(
    [switch]$SkipMigrations,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
Write-Step "ForgeLedger Test — Bootstrap (boot.ps1)"

Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not installed or not on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "  Python: $pythonVersion" -ForegroundColor Green

if (-not (Test-Command "node")) {
    Write-Host "ERROR: Node.js is not installed or not on PATH." -ForegroundColor Red
    Write-Host "Install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

$nodeVersion = node --version 2>&1
Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green

if (-not (Test-Command "npm")) {
    Write-Host "ERROR: npm is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

$npmVersion = npm --version 2>&1
Write-Host "  npm: $npmVersion" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Resolve project root (directory containing this script)
# ---------------------------------------------------------------------------
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) {
    $ProjectRoot = Get-Location
}

Write-Host "Project root: $ProjectRoot" -ForegroundColor Gray

# ---------------------------------------------------------------------------
# Load .env if present (for DATABASE_URL and other vars)
# ---------------------------------------------------------------------------
$envFile = Join-Path $ProjectRoot ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment variables from .env ..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line -split "=", 2
            if ($parts.Length -eq 2) {
                $key = $parts[0].Trim()
                $value = $parts[1].Trim().Trim('"').Trim("'")
                [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    Write-Host "  .env loaded." -ForegroundColor Green
} else {
    Write-Host "No .env file found. Checking for .env.example ..." -ForegroundColor Yellow
    $envExample = Join-Path $ProjectRoot ".env.example"
    if (Test-Path $envExample) {
        Write-Host "  .env.example found. Copy it to .env and fill in your values:" -ForegroundColor Yellow
        Write-Host "    cp .env.example .env" -ForegroundColor Gray
    } else {
        Write-Host "  No .env.example found either. Proceeding with system environment." -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# Backend: Create virtual environment and install dependencies
# ---------------------------------------------------------------------------
if (-not $FrontendOnly) {
    Write-Step "Setting up Backend (Python / FastAPI)"

    $backendDir = Join-Path $ProjectRoot "backend"
    $venvDir = Join-Path $ProjectRoot ".venv"

    # Check if backend directory exists; fall back to project root
    if (-not (Test-Path $backendDir)) {
        Write-Host "  backend/ directory not found, checking project root for requirements.txt..." -ForegroundColor Yellow
        $backendDir = $ProjectRoot
    }

    $requirementsFile = Join-Path $backendDir "requirements.txt"
    if (-not (Test-Path $requirementsFile)) {
        # Also check project root
        $requirementsFile = Join-Path $ProjectRoot "requirements.txt"
    }

    if (-not (Test-Path $requirementsFile)) {
        Write-Host "ERROR: requirements.txt not found." -ForegroundColor Red
        exit 1
    }

    Write-Host "  requirements.txt: $requirementsFile" -ForegroundColor Gray

    # Create virtual environment if it doesn't exist
    if (-not (Test-Path $venvDir)) {
        Write-Host "  Creating Python virtual environment at .venv/ ..." -ForegroundColor Yellow
        python -m venv $venvDir
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
            exit 1
        }
        Write-Host "  Virtual environment created." -ForegroundColor Green
    } else {
        Write-Host "  Virtual environment already exists at .venv/" -ForegroundColor Green
    }

    # Determine activation and pip paths
    if ($IsLinux -or $IsMacOS) {
        $pipPath = Join-Path $venvDir "bin/pip"
        $pythonPath = Join-Path $venvDir "bin/python"
        $alembicPath = Join-Path $venvDir "bin/alembic"
        $uvicornPath = Join-Path $venvDir "bin/uvicorn"
    } else {
        $pipPath = Join-Path $venvDir "Scripts/pip.exe"
        $pythonPath = Join-Path $venvDir "Scripts/python.exe"
        $alembicPath = Join-Path $venvDir "Scripts/alembic.exe"
        $uvicornPath = Join-Path $venvDir "Scripts/uvicorn.exe"
    }

    # Upgrade pip
    Write-Host "  Upgrading pip ..." -ForegroundColor Yellow
    & $pythonPath -m pip install --upgrade pip --quiet 2>&1 | Out-Null

    # Install dependencies
    Write-Host "  Installing Python dependencies from requirements.txt ..." -ForegroundColor Yellow
    & $pipPath install -r $requirementsFile --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Python dependencies." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Python dependencies installed." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Frontend: Install npm dependencies
# ---------------------------------------------------------------------------
if (-not $BackendOnly) {
    Write-Step "Setting up Frontend (React / TypeScript / Vite)"

    $frontendDir = Join-Path $ProjectRoot "frontend"

    if (-not (Test-Path $frontendDir)) {
        Write-Host "  frontend/ not found, checking web/ ..." -ForegroundColor Yellow
        $frontendDir = Join-Path $ProjectRoot "web"
    }

    if (-not (Test-Path $frontendDir)) {
        Write-Host "WARNING: No frontend directory found (frontend/ or web/). Skipping frontend setup." -ForegroundColor Yellow
    } else {
        $packageJson = Join-Path $frontendDir "package.json"
        if (-not (Test-Path $packageJson)) {
            Write-Host "WARNING: No package.json found in $frontendDir. Skipping frontend setup." -ForegroundColor Yellow
        } else {
            Write-Host "  Frontend directory: $frontendDir" -ForegroundColor Gray
            Push-Location $frontendDir
            try {
                Write-Host "  Installing npm dependencies ..." -ForegroundColor Yellow
                npm install
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "ERROR: npm install failed." -ForegroundColor Red
                    exit 1
                }
                Write-Host "  npm dependencies installed." -ForegroundColor Green
            } finally {
                Pop-Location
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Database: Run Alembic migrations
# ---------------------------------------------------------------------------
if (-not $FrontendOnly -and -not $SkipMigrations) {
    Write-Step "Running Database Migrations (Alembic)"

    $databaseUrl = [System.Environment]::GetEnvironmentVariable("DATABASE_URL", "Process")

    if (-not $databaseUrl) {
        Write-Host "WARNING: DATABASE_URL is not set. Skipping migrations." -ForegroundColor Yellow
        Write-Host "  Set DATABASE_URL in your .env file to enable database migrations." -ForegroundColor Yellow
        Write-Host "  Example: DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require" -ForegroundColor Yellow
    } else {
        # Find alembic.ini — check backend/ first, then project root
        $alembicIni = Join-Path $backendDir "alembic.ini"
        if (-not (Test-Path $alembicIni)) {
            $alembicIni = Join-Path $ProjectRoot "alembic.ini"
        }

        if (-not (Test-Path $alembicIni)) {
            Write-Host "WARNING: alembic.ini not found. Skipping migrations." -ForegroundColor Yellow
        } else {
            $alembicDir = Split-Path $alembicIni -Parent
            Write-Host "  alembic.ini: $alembicIni" -ForegroundColor Gray
            Write-Host "  Running from: $alembicDir" -ForegroundColor Gray

            Push-Location $alembicDir
            try {
                # Set PYTHONPATH so alembic can find app modules
                $env:PYTHONPATH = $alembicDir

                Write-Host "  Running alembic upgrade head ..." -ForegroundColor Yellow

                if (Test-Path $alembicPath) {
                    & $alembicPath upgrade head
                } else {
                    & $pythonPath -m alembic upgrade head
                }

                if ($LASTEXITCODE -ne 0) {
                    Write-Host "WARNING: Alembic migration failed (exit code $LASTEXITCODE)." -ForegroundColor Yellow
                    Write-Host "  This may be expected if no migrations exist yet." -ForegroundColor Yellow
                    Write-Host "  Continuing with server startup..." -ForegroundColor Yellow
                } else {
                    Write-Host "  Migrations completed successfully." -ForegroundColor Green
                }
            } finally {
                Pop-Location
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Start dev servers concurrently
# ---------------------------------------------------------------------------
Write-Step "Starting Development Servers"

$jobs = @()

# Start Backend (uvicorn)
if (-not $FrontendOnly) {
    Write-Host "  Starting backend (uvicorn) on port 8000 ..." -ForegroundColor Yellow

    # Determine the working directory for the backend
    $backendWorkDir = $backendDir
    # Check if app/ module exists relative to backend dir
    $appModule = Join-Path $backendWorkDir "app"
    if (-not (Test-Path $appModule)) {
        $appModule = Join-Path $ProjectRoot "app"
        if (Test-Path $appModule) {
            $backendWorkDir = $ProjectRoot
        }
    }

    $backendJob = Start-Job -Name "Backend" -ScriptBlock {
        param($WorkDir, $PythonExe)
        Set-Location $WorkDir

        # Pass through environment variables
        $env:PYTHONPATH = $WorkDir

        & $PythonExe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1
    } -ArgumentList $backendWorkDir, $pythonPath

    $jobs += $backendJob
    Write-Host "  Backend job started (ID: $($backendJob.Id))" -ForegroundColor Green
}

# Start Frontend (Vite dev server)
if (-not $BackendOnly -and (Test-Path $frontendDir)) {
    Write-Host "  Starting frontend (Vite) on port 5173 ..." -ForegroundColor Yellow

    $frontendJob = Start-Job -Name "Frontend" -ScriptBlock {
        param($WorkDir)
        Set-Location $WorkDir
        npm run dev 2>&1
    } -ArgumentList $frontendDir

    $jobs += $frontendJob
    Write-Host "  Frontend job started (ID: $($frontendJob.Id))" -ForegroundColor Green
}

if ($jobs.Length -eq 0) {
    Write-Host "No servers to start." -ForegroundColor Yellow
    exit 0
}

# ---------------------------------------------------------------------------
# Display access info
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ForgeLedger Test — Dev Servers Running" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if (-not $FrontendOnly) {
    Write-Host "  Backend API:    http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:       http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Health Check:   http://localhost:8000/health" -ForegroundColor White
}
if (-not $BackendOnly -and (Test-Path $frontendDir)) {
    Write-Host "  Frontend:       http://localhost:5173" -ForegroundColor White
}

Write-Host ""
Write-Host "  Press Ctrl+C to stop all servers." -ForegroundColor Yellow
Write-Host ""

# ---------------------------------------------------------------------------
# Stream output from jobs and wait for Ctrl+C
# ---------------------------------------------------------------------------
try {
    while ($true) {
        foreach ($job in $jobs) {
            $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
            if ($output) {
                $prefix = if ($job.Name -eq "Backend") { "[API]" } else { "[WEB]" }
                $color = if ($job.Name -eq "Backend") { "Cyan" } else { "Magenta" }
                foreach ($line in $output) {
                    Write-Host "$prefix $line" -ForegroundColor $color
                }
            }

            # Check if job has stopped unexpectedly
            if ($job.State -eq "Failed" -or $job.State -eq "Completed") {
                Write-Host ""
                Write-Host "WARNING: $($job.Name) server stopped unexpectedly (State: $($job.State))." -ForegroundColor Red
                $errorOutput = Receive-Job -Job $job -ErrorAction SilentlyContinue
                if ($errorOutput) {
                    foreach ($line in $errorOutput) {
                        Write-Host "  $line" -ForegroundColor Red
                    }
                }
            }
        }

        Start-Sleep -Milliseconds 500
    }
} finally {
    # Cleanup: Stop all jobs on exit
    Write-Host ""
    Write-Host "Shutting down dev servers ..." -ForegroundColor Yellow

    foreach ($job in $jobs) {
        if ($job.State -eq "Running") {
            Stop-Job -Job $job -ErrorAction SilentlyContinue
            Write-Host "  Stopped $($job.Name) server." -ForegroundColor Yellow
        }
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }

    Write-Host "All servers stopped. Goodbye!" -ForegroundColor Green
}
