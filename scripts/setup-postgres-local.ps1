<#
.SYNOPSIS
  Configure local (non-Docker) PostgreSQL instance for Project Aura.

.DESCRIPTION
  Creates database and user if not present, applies schema from scripts/init-postgres.sql,
  and updates .env with connection settings. Assumes PostgreSQL is installed and psql is on PATH.

.PARAMETER DbName
  Target database name (default: finnovate)

.PARAMETER DbUser
  Application user name (default: admin)

.PARAMETER DbPassword
  Password for the application user (default: hackathon2025)

.PARAMETER SuperPassword
  Password for the SuperUser. If omitted, psql will prompt (interactive sessions only).

.PARAMETER SuperUser
  Local PostgreSQL superuser to run DDL (default: postgres)

.PARAMETER PostgresHost
  Hostname (default: localhost)

.PARAMETER Port
  Port (default: 5432)

.PARAMETER DryRun
  If set, only prints planned actions.

.EXAMPLE
  powershell -File .\scripts\setup-postgres-local.ps1

.EXAMPLE
  powershell -File .\scripts\setup-postgres-local.ps1 -DbName finnovate_dev -DryRun

.NOTES
  Requires: psql client, local PostgreSQL server running.
#>
param(
  [string]$DbName = "finnovate",
  [string]$DbUser = "admin",
  [string]$DbPassword = "hackathon2025",
  [string]$SuperUser = "postgres",
  [string]$SuperPassword,
  [string]$PostgresHost = "localhost",
  [int]$Port = 5432,
  [switch]$DryRun
)

function Write-Step($msg) { Write-Host "[STEP] $msg" -ForegroundColor Cyan }
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor DarkGray }
function Write-Ok($msg) { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR ] $msg" -ForegroundColor Red }

function Test-Command($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Invoke-Psql {
  param(
    [string]$User,
    [string]$Db,
    [string]$Command,
    [string]$File,
    [string]$Password
  )
  $args = @('-h', $PostgresHost, '-p', "$Port", '-U', $User)
  if ($Db) { $args += @('-d', $Db) }
  if ($Command) { $args += @('-c', $Command) }
  if ($File) { $args += @('-f', $File) }
  if ($DryRun) {
    Write-Info ("DryRun: psql " + ($args -join ' '))
    return @{ ExitCode = 0; Output = '' }
  }
  $prevPwd = $env:PGPASSWORD
  if ($Password) { $env:PGPASSWORD = $Password }
  try {
    $output = & psql @args 2>&1
    $code = $LASTEXITCODE
    return @{ ExitCode = $code; Output = $output }
  }
  finally {
    $env:PGPASSWORD = $prevPwd
  }
}

if (-not (Test-Command "psql")) {
  Write-Err "psql not found. Install PostgreSQL and ensure psql is on PATH."
  exit 1
}

function SecureStringToPlain([SecureString]$sec) {
  if (-not $sec) { return $null }
  $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
  try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

$superPwdPlain = SecureStringToPlain $SuperPassword

Write-Step "Checking server connectivity"
$conn = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Command "SELECT 1;"
if ($conn.ExitCode -ne 0) { Write-Err "Cannot connect with superuser '$SuperUser'. Ensure server is running and credentials are correct."; exit 1 } else { Write-Ok "Server reachable." }

Write-Step "Ensure database [$DbName] exists"
$dbExists = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Command "\pset tuples_only on; SELECT 1 FROM pg_database WHERE datname='$DbName';"
if (-not $DryRun) {
  if (-not ($dbExists.Output | Select-String -SimpleMatch '1')) {
    Write-Info "Creating database $DbName"
    $crt = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Command "CREATE DATABASE $DbName;"
    if ($crt.ExitCode -ne 0) { Write-Err "Failed to create database"; exit 1 }
  }
  else { Write-Ok "Database already exists." }
}

Write-Step "Ensure role/user [$DbUser] exists"
$userExists = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Command "\pset tuples_only on; SELECT 1 FROM pg_roles WHERE rolname='$DbUser';"
if (-not $DryRun) {
  if (-not ($userExists.Output | Select-String -SimpleMatch '1')) {
    Write-Info "Creating role $DbUser"
    $crtUser = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Command "CREATE ROLE $DbUser LOGIN PASSWORD '$DbPassword';"
    if ($crtUser.ExitCode -ne 0) { Write-Err "Failed to create role"; exit 1 }
    $null = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Command "GRANT CONNECT ON DATABASE $DbName TO $DbUser;"
  }
  else { Write-Ok "Role already exists." }
}

Write-Step "Apply schema from scripts/init-postgres.sql"
$schemaFile = Join-Path $PSScriptRoot "init-postgres.sql"
if (-not (Test-Path $schemaFile)) { Write-Err "Schema file not found: $schemaFile"; exit 1 }
$apply = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Db $DbName -File $schemaFile
if (-not $DryRun -and $apply.ExitCode -ne 0) { Write-Err "Schema apply failed"; Write-Info $apply.Output; exit 1 } elseif (-not $DryRun) { Write-Ok "Schema applied." }

Write-Step "Grant privileges (basic)"
$grantCmds = @(
  "GRANT USAGE ON SCHEMA public TO $DbUser;",
  "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $DbUser;",
  "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $DbUser;"
)
foreach ($gc in $grantCmds) {
  $res = Invoke-Psql -User $SuperUser -Password $superPwdPlain -Db $DbName -Command $gc
  if (-not $DryRun -and $res.ExitCode -ne 0) { Write-Warn "Grant failed: $gc" }
}
Write-Ok "Privileges granted."

$envPath = Join-Path (Get-Location) ".env"
$envLines = @()
if (Test-Path $envPath) { $envLines = Get-Content $envPath }
$envMap = @{
  "POSTGRES_HOST"     = $PostgresHost;
  "POSTGRES_PORT"     = $Port;
  "POSTGRES_DB"       = $DbName;
  "POSTGRES_USER"     = $DbUser;
  "POSTGRES_PASSWORD" = $DbPassword
}
foreach ($k in $envMap.Keys) {
  $pattern = "^$k=.*$"
  $line = "$k=$($envMap[$k])"
  if ($DryRun) {
    Write-Info "DryRun: would set $line"
  }
  else {
    if ($envLines -match $pattern) {
      $envLines = $envLines -replace $pattern, $line
    }
    else {
      $envLines += $line
    }
  }
}
if (-not $DryRun) { $envLines | Set-Content $envPath; Write-Ok ".env updated." }

Write-Step "Connection test with app user"
$appTest = Invoke-Psql -User $DbUser -Password $DbPassword -Db $DbName -Command "SELECT COUNT(*) FROM information_schema.tables;"
if (-not $DryRun -and $appTest.ExitCode -ne 0) { Write-Err "App user connectivity failed."; Write-Info $appTest.Output; exit 1 } elseif (-not $DryRun) { Write-Ok "App user connectivity verified." }

Write-Ok "Local PostgreSQL configuration complete."