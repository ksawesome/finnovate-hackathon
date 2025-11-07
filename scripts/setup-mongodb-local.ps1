<#
.SYNOPSIS
  Configure local (non-Docker) MongoDB for Project Aura tri-store.

.DESCRIPTION
  Verifies mongosh availability, checks server connectivity, optionally enables auth user,
  initializes baseline collections & indexes expected by src/db/mongodb.py, and updates .env.
  By default assumes no authentication (MongoDB Community fresh install). Use -EnableAuth to
  create an application user and print instructions to enable authorization in mongod.cfg.

.PARAMETER DbName
  Target database name (default: finnovate)

.PARAMETER Host
  Hostname (default: localhost)

.PARAMETER Port
  Port (default: 27017)

.PARAMETER EnableAuth
  Switch: create application user & add credentials to .env. You must manually enable security.authorization afterwards.

.PARAMETER AppUser
  MongoDB application user (default: admin) used when -EnableAuth is set.

.PARAMETER AppPassword
  Application user password (default: hackathon2025) used when -EnableAuth is set.

.PARAMETER DryRun
  Show planned operations without executing.

.EXAMPLE
  powershell -File .\scripts\setup-mongodb-local.ps1

.EXAMPLE
  powershell -File .\scripts\setup-mongodb-local.ps1 -EnableAuth -AppUser aura_mongo -AppPassword S3cret!

.NOTES
  Requires: mongosh on PATH. If you installed only the legacy mongo shell, adjust commands accordingly.
#>
param(
    [string]$DbName = "finnovate",
    [string]$MongoHost = "localhost",
    [int]$MongoPort = 27017,
    [switch]$EnableAuth,
    [string]$AppUser = "admin",
    [SecureString]$AppPassword,
    [switch]$DryRun
)

function Write-Step($m) { Write-Host "[STEP] $m" -ForegroundColor Cyan }
function Write-Ok($m) { Write-Host "[ OK ] $m" -ForegroundColor Green }
function Write-Info($m) { Write-Host "[INFO] $m" -ForegroundColor DarkGray }
function Write-Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m) { Write-Host "[ERR ] $m" -ForegroundColor Red }

function Test-Command($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

if (-not (Test-Command "mongosh")) { Write-Err "mongosh not found. Install MongoDB Community Server and ensure mongosh on PATH."; exit 1 }

$baseArgs = @('--host', $MongoHost, '--port', $MongoPort)

function Invoke-MongoshScript {
    param([string]$Script)
    if ($DryRun) { Write-Info "DryRun: mongosh $($baseArgs -join ' ') --eval \"$Script\""; return @{ExitCode = 0; Output = '' } }
    $out = & mongosh @baseArgs --quiet --eval $Script 2>&1
    $code = $LASTEXITCODE
    return @{ExitCode = $code; Output = $out }
}

Write-Step "Connectivity check"
$ping = Invoke-MongoshScript -Script "db.runCommand({ ping: 1 })"
if ($ping.ExitCode -ne 0) { Write-Err ("MongoDB not reachable on ${MongoHost}:${MongoPort}"); Write-Info $ping.Output; exit 1 } else { Write-Ok "Server reachable." }

Write-Step "Database presence (auto-created on first write)"
# Listing databases; finnovate may not appear yet.
$show = Invoke-MongoshScript -Script "db.adminCommand({ listDatabases: 1 })"
if ($show.Output -match $DbName) { Write-Ok "Database $DbName already visible." } else { Write-Info "Database $DbName will appear after first collection insert." }

Write-Step "Initialize collections & indexes"
$initScript = @"
use $DbName;
// supporting_docs
db.supporting_docs.createIndex({ gl_code: 1 });
db.supporting_docs.createIndex({ gl_code: 1, period: 1 });
// audit_trail
db.audit_trail.createIndex({ gl_code: 1 });
db.audit_trail.createIndex({ timestamp: 1 });
db.audit_trail.createIndex({ gl_code: 1, timestamp: -1 });
// validation_results
db.validation_results.createIndex({ gl_code: 1 });
db.validation_results.createIndex({ validation_suite: 1 });
// seed minimal audit event to force DB creation
if (db.audit_trail.countDocuments({}) === 0) { db.audit_trail.insertOne({ gl_code: 'SEED', action: 'init', actor: { system: true }, timestamp: new Date() }); }
"@
$init = Invoke-MongoshScript -Script $initScript
if ($init.ExitCode -ne 0) { Write-Err "Collection/index init failed"; Write-Info $init.Output; exit 1 } else { Write-Ok "Collections & indexes initialized." }

function SecureStringToPlain([SecureString]$sec) {
    if (-not $sec) { return $null }
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

if ($EnableAuth) {
    Write-Step "Create application user (requires auth disabled currently)"
    $userScript = @"
use $DbName;
if (!db.getUser('$AppUser')) {
  db.createUser({ user: '$AppUser', pwd: '$((SecureStringToPlain $AppPassword))', roles: [ { role: 'readWrite', db: '$DbName' } ] });
}
"@
    $usr = Invoke-MongoshScript -Script $userScript
    if ($usr.ExitCode -ne 0) { Write-Err "User creation failed"; Write-Info $usr.Output; exit 1 } else { Write-Ok "User ensured: $AppUser" }
    $authMsg = @()
    $authMsg += "Authorization still OFF. To enable:"
    $authMsg += "1) Edit mongod.cfg and add:\n   security:\n     authorization: enabled"
    $authMsg += "2) Restart the MongoDB service."
    $authMsg += ("3) Connect with: mongodb://${AppUser}:<password>@${MongoHost}:${MongoPort}/${DbName}")
    Write-Warn ($authMsg -join "`n")
}

Write-Step "Update .env"
$envPath = Join-Path (Get-Location) ".env"
$envLines = @()
if (Test-Path $envPath) { $envLines = Get-Content $envPath }
$envMap = @{ "MONGO_HOST" = $MongoHost; "MONGO_PORT" = $MongoPort; "MONGO_DB" = $DbName }
if ($EnableAuth) { $envMap["MONGO_USER"] = $AppUser; $envMap["MONGO_PASSWORD"] = (SecureStringToPlain $AppPassword) }
foreach ($k in $envMap.Keys) {
    $pattern = "^$k=.*$"; $line = "$k=$($envMap[$k])"
    if ($DryRun) { Write-Info "DryRun: would set $line" }
    else {
        if ($envLines -match $pattern) { $envLines = $envLines -replace $pattern, $line } else { $envLines += $line }
    }
}
if (-not $DryRun) { $envLines | Set-Content $envPath; Write-Ok ".env updated." }

Write-Step "Verification"
$verify = Invoke-MongoshScript -Script "use $DbName; db.getCollectionNames()"
if ($verify.ExitCode -ne 0) { Write-Err "Verification failed"; Write-Info $verify.Output; exit 1 }
Write-Ok "Collections: $($verify.Output -split '\n' | Where-Object { $_ -match '\S' } | ForEach-Object { $_ } )"

Write-Ok "Local MongoDB configuration complete."