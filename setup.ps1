# BookMe.ma Setup Script
# Run this script to set up the development environment

Write-Host "🚀 Setting up BookMe.ma Development Environment" -ForegroundColor Blue
Write-Host ""

# --- Function for safe command execution ---
function Run-Command {
    param (
        [string]$Command,
        [string]$ErrorMessage
    )
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed"
        }
    } catch {
        Write-Host "✗ $ErrorMessage" -ForegroundColor Red
        exit 1
    }
}

# --- Check Python version ---
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersionOutput = & python --version 2>&1
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11.x." -ForegroundColor Red
    exit 1
}

# Extract numeric version, e.g. "3.11.8" → 3.11
if ($pythonVersionOutput -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -eq 3 -and $minor -eq 11) {
        Write-Host "✓ Python version OK: $pythonVersionOutput" -ForegroundColor Green
    } else {
        Write-Host "✗ Python 3.11.x required. Found: $pythonVersionOutput" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Could not parse Python version output: $pythonVersionOutput" -ForegroundColor Red
    exit 1
}


# --- Check Docker ---
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = & docker --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Docker not found" }
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# --- Create .env from example ---
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Creating .env file..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✓ .env file created. Please update with your values." -ForegroundColor Green
    } else {
        Write-Host "✗ .env.example not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# --- Create logs directory ---
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✓ logs directory created" -ForegroundColor Green
}

# --- Create virtual environment ---
Write-Host ""
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    Run-Command "python -m venv venv" "Failed to create virtual environment"
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# --- Activate virtual environment ---
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Host "✗ Could not find virtual environment activation script at $venvActivate" -ForegroundColor Red
    exit 1
}

# --- Install dependencies ---
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Run-Command "pip install --upgrade pip setuptools wheel" "Failed to upgrade pip or setuptools"
Run-Command "pip install -e .[dev]" "Failed to install Python dependencies"
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# --- Install pre-commit hooks ---
Write-Host ""
Write-Host "Installing pre-commit hooks..." -ForegroundColor Yellow
Run-Command "pre-commit install" "Failed to install pre-commit hooks"
Write-Host "✓ Pre-commit hooks installed" -ForegroundColor Green

# --- Start Docker services ---
Write-Host ""
Write-Host "Starting Docker services..." -ForegroundColor Yellow
Run-Command "docker-compose up -d db redis" "Failed to start Docker services"
Write-Host "Waiting for services to be ready..."
Start-Sleep -Seconds 10
Write-Host "✓ Docker services started" -ForegroundColor Green

# --- Run migrations ---
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Yellow
Run-Command "python src/manage.py migrate_schemas --shared" "Migration failed"
Write-Host "✓ Migrations completed" -ForegroundColor Green

# --- Create superuser prompt ---
Write-Host ""
Write-Host "Would you like to create a superuser? (Y/N)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -match "^[Yy]$") {
    Run-Command "python src/manage.py createsuperuser" "Failed to create superuser"
}

# --- Summary ---
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update .env file with your configuration"
Write-Host "  2. Run: docker-compose up -d"
Write-Host "  3. Run: python src/manage.py runserver"
Write-Host ""
Write-Host "Access points:" -ForegroundColor Yellow
Write-Host "  • API:        http://localhost:8000/api/v1/"
Write-Host "  • Admin:      http://localhost:8000/admin/"
Write-Host "  • API Docs:   http://localhost:8000/api/docs/"
Write-Host "  • Flower:     http://localhost:5555/"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  • make help              - Show all available commands"
Write-Host "  • make dev               - Start development environment"
Write-Host "  • make test              - Run tests"
Write-Host "  • make lint              - Run linting"
Write-Host ""
