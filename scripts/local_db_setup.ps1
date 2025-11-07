# Local database setup (no Docker) for Project Aura
# - Ensures PostgreSQL role/db exist and applies schema from scripts/init-postgres.sql
# - Initializes MongoDB collections and indexes via Python
#
# Usage (PowerShell):
#   # Optional: customize via parameters or env vars
#   .\scripts\local_db_setup.ps1 -PgHost localhost -PgPort 5432 -PgDb finnovate -PgUser admin -PgPassword hackathon2025 -MongoHost localhost -MongoPort 27017 -MongoDb finnovate

[CmdletBinding()]
param(
  [string]$PgHost = 'localhost',
  [int]$PgPort = 5432,
  [string]$PgDb = 'finnovate',
  [string]$PgUser = 'admin',
  [string]$PgPassword = 'hackathon2025',
  [string]$MongoHost = 'localhost',
  [int]$MongoPort = 27017,
  [string]$MongoDb = 'finnovate'
)

# Override with env vars if set
if ($env:POSTGRES_HOST) { $PgHost = $env:POSTGRES_HOST }
if ($env:POSTGRES_PORT) { $PgPort = [int]$env:POSTGRES_PORT }
if ($env:POSTGRES_DB) { $PgDb = $env:POSTGRES_DB }
if ($env:POSTGRES_USER) { $PgUser = $env:POSTGRES_USER }
if ($env:POSTGRES_PASSWORD) { $PgPassword = $env:POSTGRES_PASSWORD }
if ($env:MONGO_HOST) { $MongoHost = $env:MONGO_HOST }
if ($env:MONGO_PORT) { $MongoPort = [int]$env:MONGO_PORT }
if ($env:MONGO_DB) { $MongoDb = $env:MONGO_DB }

Write-Host "=== Local DB Setup (no Docker) ===" -ForegroundColor Cyan

# Resolve repo root and SQL path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SqlPath = Join-Path $RepoRoot 'scripts\init-postgres.sql'

if (!(Test-Path $SqlPath)) {
  Write-Host "[PostgreSQL] ERROR: SQL init file not found at $SqlPath" -ForegroundColor Red
  exit 1
}

# Ensure psql available
$psql = 'psql'
try {
  $null = & $psql --version 2>$null
}
catch {
  # Try default Windows installation path
  $defaultPsql = 'C:\Program Files\PostgreSQL\16\bin\psql.exe'
  if (Test-Path $defaultPsql) { $psql = $defaultPsql } else {
    Write-Host "[PostgreSQL] ERROR: psql not found in PATH. Add PostgreSQL bin to PATH or set full path in script." -ForegroundColor Red
    exit 1
  }
}

Write-Host "[PostgreSQL] Using host=$PgHost port=$PgPort db=$PgDb user=$PgUser" -ForegroundColor Yellow

# Create role (admin) if not exists and grant CREATEDB
$env:PGPASSWORD = $PgPassword
& $psql -h $PgHost -p $PgPort -U postgres -d postgres -v ON_ERROR_STOP=1 -c @"
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$PgUser') THEN
    EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L', '$PgUser', '$PgPassword');
    EXECUTE format('ALTER ROLE %I CREATEDB', '$PgUser');
  END IF;
END
$$;
"@
if ($LASTEXITCODE -ne 0) {
  Write-Host "[PostgreSQL] Warning: Could not ensure role via superuser. If you don't know the superuser, manually create role $PgUser." -ForegroundColor DarkYellow
}

# Create database if not exists (attempt with superuser, then with $PgUser)
& $psql -h $PgHost -p $PgPort -U postgres -d postgres -v ON_ERROR_STOP=1 -c @"
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$PgDb') THEN
    EXECUTE format('CREATE DATABASE %I OWNER %I', '$PgDb', '$PgUser');
  END IF;
END
$$;
"@
if ($LASTEXITCODE -ne 0) {
  Write-Host "[PostgreSQL] Falling back to creating DB as $PgUser (requires CREATEDB)." -ForegroundColor DarkYellow
  & $psql -h $PgHost -p $PgPort -U $PgUser -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$PgDb\";" 2>$null
}

# Apply schema/init SQL as application user
Write-Host "[PostgreSQL] Applying schema from $SqlPath ..." -ForegroundColor Yellow
& $psql -h $PgHost -p $PgPort -U $PgUser -d $PgDb -v ON_ERROR_STOP=1 -f $SqlPath
if ($LASTEXITCODE -ne 0) {
  Write-Host "[PostgreSQL] ERROR applying schema. See errors above." -ForegroundColor Red
  exit 1
}

Write-Host "[PostgreSQL] Initialization complete." -ForegroundColor Green

# Initialize MongoDB collections via Python (optional if env not ready)
Write-Host "[MongoDB] Initializing collections and indexes (host=$MongoHost port=$MongoPort db=$MongoDb)..." -ForegroundColor Yellow

# Export env vars for Python process
$env:MONGO_HOST = $MongoHost
$env:MONGO_PORT = "$MongoPort"
$env:MONGO_DB = $MongoDb

try {
  $pythonCode = @"
from src.db.mongodb import init_mongo_collections
init_mongo_collections()
print('MongoDB collections initialized')
"@
  python -c $pythonCode
  if ($LASTEXITCODE -ne 0) { throw "python returned non-zero" }
  Write-Host "[MongoDB] Initialization complete." -ForegroundColor Green
}
catch {
  Write-Host "[MongoDB] Skipped (ensure Python env with pymongo is active, then run: python -c `"from src.db.mongodb import init_mongo_collections; init_mongo_collections()`")" -ForegroundColor DarkYellow
}

Write-Host "=== Local DB Setup Complete ===" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "- Activate conda env:  conda activate finnovate-hackathon"
Write-Host "- Test PG:           python -c `"from src.db import get_postgres_engine; from sqlalchemy import text; print(get_postgres_engine().connect().execute(text('SELECT 1')).scalar())`""
Write-Host "- Test Mongo:        python -c `"from src.db import get_mongo_database; print(get_mongo_database().list_collection_names())`""
