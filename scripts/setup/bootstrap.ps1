# Bootstrap script for Windows PowerShell

Write-Host "=== Project Aura Bootstrap ===" -ForegroundColor Cyan

Write-Host "`nStep 1: Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`nStep 2: Waiting for databases to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nStep 3: Creating conda environment..." -ForegroundColor Yellow
conda env create -f environment.yml -y

Write-Host "`nStep 4: Activating environment..." -ForegroundColor Yellow
conda activate finnovate-hackathon

Write-Host "`nStep 5: Initializing PostgreSQL schema..." -ForegroundColor Yellow
# Schema is auto-initialized by Docker entrypoint

Write-Host "`nStep 6: Initializing MongoDB collections..." -ForegroundColor Yellow
python -c "from src.db.mongodb import init_mongo_collections; init_mongo_collections(); print('MongoDB collections initialized')"

Write-Host "`nStep 7: Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\raw" | Out-Null
New-Item -ItemType Directory -Force -Path "data\processed" | Out-Null
New-Item -ItemType Directory -Force -Path "data\supporting_docs" | Out-Null
New-Item -ItemType Directory -Force -Path "data\vectors" | Out-Null

Write-Host "`nStep 8: Setting up pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

Write-Host "`n=== Bootstrap Complete! ===" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "1. conda activate finnovate-hackathon"
Write-Host "2. streamlit run src/app.py"
Write-Host "`nDatabases running:"
Write-Host "- PostgreSQL: localhost:5432 (user: admin, db: finnovate)"
Write-Host "- MongoDB: localhost:27017 (db: finnovate)"