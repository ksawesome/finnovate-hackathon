# Scripts Directory

This directory contains all automation scripts organized by category for maintainability and scalability.

## 📁 Directory Structure

```
scripts/
├── README.md (this file)
├── setup/                   # Environment and infrastructure setup
│   ├── bootstrap.ps1
│   ├── local_db_setup.ps1
│   ├── setup-postgres-local.ps1
│   ├── setup-mongodb-local.ps1
│   ├── cleanup-old-diagrams.ps1
│   ├── render-diagrams.ps1
│   └── export-docs.ps1
├── database/                # Database management and initialization
│   ├── init-postgres.sql
│   ├── reset_database.py
│   └── seed_sample_data.py
└── data/                    # Data extraction and analysis
    ├── extract_trial_balance.py
    └── analyze_trial_balance.py
```

## 🚀 Quick Start

### First Time Setup
```powershell
# 1. Bootstrap environment
.\scripts\setup\bootstrap.ps1

# 2. Setup databases (PostgreSQL + MongoDB)
.\scripts\setup\local_db_setup.ps1

# 3. Seed sample data
python scripts\database\seed_sample_data.py
```

### Daily Development
```powershell
# Reset database to clean state
python scripts\database\reset_database.py

# Re-seed sample data
python scripts\database\seed_sample_data.py

# Extract Trial Balance data
python scripts\data\extract_trial_balance.py
```

---

## 📚 Script Categories

### Setup Scripts (`setup/`)
Infrastructure setup, environment configuration, and documentation tooling.

#### **bootstrap.ps1**
- **Purpose:** One-command environment setup
- **Creates:** Conda environment, installs dependencies, initializes databases
- **Usage:** `.\scripts\setup\bootstrap.ps1`
- **When to Use:** First time project setup or after major dependency changes

#### **local_db_setup.ps1**
- **Purpose:** Initialize PostgreSQL and MongoDB locally (no Docker)
- **Creates:** Databases, users, initial schema
- **Usage:** `.\scripts\setup\local_db_setup.ps1`
- **When to Use:** Database setup or after database corruption

#### **setup-postgres-local.ps1**
- **Purpose:** PostgreSQL-specific setup
- **Creates:** finnovate database, admin user, runs init-postgres.sql
- **Usage:** `.\scripts\setup\setup-postgres-local.ps1`
- **When to Use:** PostgreSQL issues or standalone PostgreSQL setup

#### **setup-mongodb-local.ps1**
- **Purpose:** MongoDB-specific setup
- **Creates:** finnovate database, admin user, creates collections
- **Usage:** `.\scripts\setup\setup-mongodb-local.ps1`
- **When to Use:** MongoDB issues or standalone MongoDB setup

#### **render-diagrams.ps1**
- **Purpose:** Generate SVG diagrams from PlantUML/Mermaid
- **Output:** Architecture diagrams in docs/
- **Usage:** `.\scripts\setup\render-diagrams.ps1`
- **When to Use:** After updating architecture diagrams

#### **export-docs.ps1**
- **Purpose:** Export documentation to PDF/HTML
- **Output:** Compiled documentation package
- **Usage:** `.\scripts\setup\export-docs.ps1`
- **When to Use:** Creating documentation deliverables

#### **cleanup-old-diagrams.ps1**
- **Purpose:** Remove outdated diagram files
- **Usage:** `.\scripts\setup\cleanup-old-diagrams.ps1`
- **When to Use:** Cleaning up after diagram updates

---

### Database Scripts (`database/`)
Database schema management, data seeding, and reset utilities.

#### **init-postgres.sql**
- **Purpose:** PostgreSQL schema initialization SQL
- **Creates:** All 7 tables with indexes and constraints
- **Usage:** Executed by setup-postgres-local.ps1
- **When to Use:** Manual database initialization or reference

#### **reset_database.py**
- **Purpose:** Drop and recreate all PostgreSQL tables
- **Warning:** ⚠️ DESTROYS ALL DATA
- **Usage:** `python scripts\database\reset_database.py`
- **When to Use:** 
  - After schema changes in src/db/postgres.py
  - Clean slate for testing
  - Database corruption recovery

**Example:**
```python
from src.db.postgres import Base
from src.db import get_postgres_engine

# Drops all tables
Base.metadata.drop_all(engine)

# Recreates with new schema
Base.metadata.create_all(engine)
```

#### **seed_sample_data.py**
- **Purpose:** Populate databases with sample data for testing
- **Creates:** 24+ records across PostgreSQL and MongoDB
- **Usage:** `python scripts\database\seed_sample_data.py`
- **When to Use:** 
  - After database reset
  - Testing CRUD operations
  - Validating data flow
  - Demo preparation

**Sample Data Seeded:**
- 5 users (Finance, Treasury, Accounts)
- 5 GL accounts (Cash, Receivables, Payables, Revenue, Expenses)
- 5 responsibility assignments
- 2 master chart accounts
- 2 account templates
- 2 query templates
- 2 user feedback items

**Validation:**
```sql
-- PostgreSQL
SELECT u.name, COUNT(ga.id) as accounts 
FROM users u 
LEFT JOIN gl_accounts ga ON u.id = ga.assigned_user_id 
GROUP BY u.name;

-- MongoDB
db.gl_metadata.countDocuments()
db.assignment_details.countDocuments()
```

---

### Data Scripts (`data/`)
Data extraction, transformation, and analysis utilities.

#### **extract_trial_balance.py**
- **Purpose:** Extract and clean Trial Balance data from Excel to CSV
- **Input:** Trial Balance Excel file (12 sheets)
- **Output:** `data/sample/trial_balance_cleaned.csv` (501 records)
- **Usage:** `python scripts\data\extract_trial_balance.py`
- **When to Use:** 
  - Updating sample data from new Excel files
  - Creating test datasets
  - Data validation before ingestion

**Features:**
- Reads "Final Data" sheet (501 GL accounts)
- Maps Excel columns to database schema
- Cleans data (removes nulls, formats numbers)
- Validates required fields
- Outputs ready-to-ingest CSV

**Example:**
```python
# Extracts from Excel
df = pd.read_excel('Trial_Balance.xlsx', sheet_name='Final Data')

# Maps columns
df_cleaned = df.rename(columns={
    'GL Code': 'account_code',
    'GL Account Name': 'account_name',
    # ... 17 more mappings
})

# Saves to CSV
df_cleaned.to_csv('data/sample/trial_balance_cleaned.csv', index=False)
```

#### **analyze_trial_balance.py**
- **Purpose:** Comprehensive analysis of all 12 Trial Balance sheets
- **Output:** Analysis report with statistics and relevance scoring
- **Usage:** `python scripts\data\analyze_trial_balance.py`
- **When to Use:** 
  - Understanding new Excel files
  - Validating data structures
  - Creating documentation

**Analysis Includes:**
- Sheet-by-sheet row/column counts
- Data type detection
- Null value analysis
- Relevance scoring (1-10)
- Usage recommendations
- Sample data preview

---

## 🎯 Common Workflows

### Workflow 1: Clean Slate Development
```powershell
# Reset everything and start fresh
python scripts\database\reset_database.py
python scripts\database\seed_sample_data.py

# Verify
python -c "from src.db.postgres import get_gl_accounts_by_period; print(len(get_gl_accounts_by_period('Mar-24')))"
# Expected: 5
```

### Workflow 2: Update Sample Data
```powershell
# Extract new data from Excel
python scripts\data\extract_trial_balance.py

# Reset and reload
python scripts\database\reset_database.py
python scripts\database\seed_sample_data.py
```

### Workflow 3: Schema Changes
```powershell
# 1. Modify src/db/postgres.py models
# 2. Reset database with new schema
python scripts\database\reset_database.py

# 3. Re-seed sample data
python scripts\database\seed_sample_data.py

# 4. Validate changes
python -c "from src.db.postgres import Base; print(Base.metadata.tables.keys())"
```

### Workflow 4: Fresh Project Setup
```powershell
# Complete setup from scratch
.\scripts\setup\bootstrap.ps1
.\scripts\setup\local_db_setup.ps1
python scripts\database\seed_sample_data.py

# Verify environment
python -c "from src.db import get_postgres_engine, get_mongo_database; print('✅ Databases connected')"
```

---

## 🔒 Safety & Best Practices

### ⚠️ Destructive Operations
These scripts **DELETE DATA** - use with caution:
- `reset_database.py` - Drops all PostgreSQL tables
- `cleanup-old-diagrams.ps1` - Deletes old diagram files

**Always:**
1. Commit changes to git before running
2. Backup production databases before reset
3. Verify you're targeting the correct database

### 🧪 Testing Scripts
Before running on production data:
1. Test with sample data first
2. Verify output manually
3. Check database connection strings
4. Review `.env` file for correct credentials

### 📝 Adding New Scripts
When creating new scripts:
1. **Place in appropriate category** (setup/, database/, data/)
2. **Add to this README** with purpose, usage, and examples
3. **Include error handling** and user feedback
4. **Document prerequisites** (databases, files, permissions)
5. **Add success criteria** (what to verify after running)

---

## 📊 Script Metrics

| Script | Lines | Purpose | Frequency |
|--------|-------|---------|-----------|
| seed_sample_data.py | 600+ | Data seeding | Daily (dev) |
| extract_trial_balance.py | 200+ | Data extraction | Weekly |
| reset_database.py | 30 | DB reset | Daily (dev) |
| analyze_trial_balance.py | 150+ | Data analysis | As needed |
| bootstrap.ps1 | 100+ | Environment setup | Once |
| local_db_setup.ps1 | 80+ | DB setup | Once |

---

## 🛠️ Prerequisites

### For Setup Scripts
- PowerShell 5.1+
- Conda/Miniconda installed
- PostgreSQL 16+ installed
- MongoDB 7.0+ installed

### For Python Scripts
- Conda environment activated: `conda activate finnovate-hackathon`
- Databases running (check with `psql` and `mongosh`)
- `.env` file configured with database credentials

### For Data Scripts
- Trial Balance Excel file in project root
- Write permissions to `data/sample/` directory

---

## 📞 Troubleshooting

### Script Fails with "Database connection error"
```powershell
# Check if databases are running
Get-Process -Name postgres,mongod

# Verify connection strings in .env
cat .env | Select-String "POSTGRES|MONGO"

# Test connection
python -c "from src.db import get_postgres_engine; print(get_postgres_engine().connect())"
```

### "Permission denied" errors
```powershell
# Run PowerShell as Administrator
# Or check file permissions
icacls scripts\database\seed_sample_data.py
```

### Sample data seeding fails
```powershell
# Reset database first
python scripts\database\reset_database.py

# Then re-seed
python scripts\database\seed_sample_data.py
```

---

**Maintained by:** Project Aura Team  
**Last Updated:** November 7, 2025  
**Total Scripts:** 11 scripts across 3 categories
