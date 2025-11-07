# GitHub Copilot Instructions for Project Aura

## Project Overview
**Project Aura** is an AI-powered financial statement review agent built for the Adani Group's 1,000+ entity finance operations. It automates GL account validation, consolidation, and reporting using a tri-store architecture (PostgreSQL, MongoDB, file system).

## Architecture: Tri-Store System

### Data Storage Strategy
- **PostgreSQL** (`src/db/postgres.py`): Structured financial data (Users, GLAccount, ResponsibilityMatrix, ReviewLog)
- **MongoDB** (`src/db/mongodb.py`): Semi-structured metadata (supporting_docs, audit_trail, validation_results)
- **File System** (`src/db/storage.py`): Raw CSVs (`data/raw/`), Parquet cache (`data/processed/`), supporting docs (`data/supporting_docs/`), ChromaDB vectors (`data/vectors/`)

**Key Pattern**: All DB connections use env-var-driven singletons from `src/db/__init__.py`:
```python
from src.db import get_postgres_session, get_mongo_database
session = get_postgres_session()
db = get_mongo_database()
```

### Data Flow: CSV → PostgreSQL → MongoDB → Parquet
1. **Ingestion** (`data_ingestion.py`): CSV → `save_raw_csv()` → PostgreSQL via `create_gl_account()` → `log_audit_event()` to MongoDB
2. **Validation** (`data_validation.py`): Great Expectations suite → results to MongoDB (`save_validation_results()`)
3. **Analytics** (`analytics.py`): Query PostgreSQL → cache to Parquet via `save_processed_parquet()`

## Critical Developer Workflows

### Environment Setup (Local, No Docker)
```powershell
# Create conda environment
conda env update -f environment.yml --prune
conda activate finnovate-hackathon

# Initialize databases (PostgreSQL + MongoDB)
.\scripts\local_db_setup.ps1

# Verify connectivity
python -c "from src.db import get_postgres_engine; from sqlalchemy import text; print(get_postgres_engine().connect().execute(text('SELECT 1')).scalar())"
```

### Testing & Linting
```powershell
make lint        # ruff check
make format      # black + isort
make type-check  # mypy --strict
make test        # pytest with coverage ≥80%
```

### Running the App
```powershell
streamlit run src/app.py  # Port 8501
```

## Project-Specific Conventions

### Import Style
- **Relative imports within `src/`**: Always use `from .db import ...` or `from .db.postgres import ...`
- **External imports**: Standard library → Third-party → Local (`# Local imports` comment)
- Enforced by `isort` with `profile = "black"`

### Database Patterns
1. **PostgreSQL**: Always use context managers or close sessions explicitly
   ```python
   session = get_postgres_session()
   try:
       user = session.query(User).filter_by(email=email).first()
   finally:
       session.close()
   ```

2. **MongoDB**: Collections accessed via helper functions, not direct DB access
   ```python
   from src.db.mongodb import get_audit_trail_collection
   collection = get_audit_trail_collection()  # NOT db["audit_trail"]
   ```

3. **File Storage**: Use storage.py functions, never raw file I/O
   ```python
   from src.db.storage import save_processed_parquet, load_processed_parquet
   save_processed_parquet(df, "analytics_cache")  # Auto-handles paths
   ```

### Data Validation with Great Expectations
- **Context initialization**: Run `great_expectations init` to create the GX context directory structure before first use
- **Suite creation**: Use `create_expectation_suite()` in `data_validation.py`
- **Critical check**: Trial balance must sum to nil (Debits = Credits)
- **Results**: Always log to MongoDB via `save_validation_results(gl_code, period, results)`

### Continuous Learning Loop
- **Model**: Scikit-learn stored in MLflow (`src/ml_model.py`)
- **Feedback**: User corrections → `src/feedback_handler.py` → retrain via `train_and_log_model()`
- **Pattern**: Always log experiments to MLflow for reproducibility

### LangChain Agent Tools
- **Tool definition**: Inherit from `BaseTool` in `src/langchain_tools.py`
- **Agent creation**: Use `create_agent(tools)` from `src/agent.py`
- **Query pattern**: `query_agent(agent, natural_language_query)` returns structured response

## Integration Points

### External Dependencies
- **Gemini API**: Required for LangChain agent (set `GOOGLE_API_KEY` env var for Gemini)
- **ChromaDB**: Vector store for RAG (`src/vector_store.py`), auto-persisted to `data/vectors/`
- **MLflow**: Experiment tracking (runs locally, no server needed)

### Cross-Component Communication
- **Ingestion → Validation**: `pipeline()` in `data_ingestion.py` returns DataFrame → passed to `validate_data()`
- **Validation → Analytics**: `validate_period(period)` queries PostgreSQL, logs to MongoDB
- **Analytics → Visualizations**: `perform_analytics(period)` returns dict → `create_dashboard_charts()` in `visualizations.py`

## Phase Alignment (6-Day Plan)
- **Phase 1 (Days 1-3)**: Data pipeline (`data_ingestion.py`, PostgreSQL setup)
- **Phase 2 (Days 4-6)**: Validation (`data_validation.py`, Great Expectations, MongoDB)
- **Phase 3 (Days 7-9)**: ML & Agent (`ml_model.py`, `agent.py`, LangChain tools)
- **Phase 4 (Days 10-12)**: UI (`app.py`, Streamlit, Plotly visualizations)
- **Phase 5 (Days 13-15)**: Integration, testing, demo prep

## Key Files to Understand
- `src/db/__init__.py`: Connection management (all env vars defined here)
- `src/data_ingestion.py`: Complete CSV → PostgreSQL → MongoDB flow
- `scripts/init-postgres.sql`: Database schema (tables, indexes, seed data)
- `docs/Storage-Architecture.md`: Comprehensive tri-store documentation
- `environment.yml`: Conda dependencies (Python 3.11, all packages)
- `data/sample/`: Sample CSV files for testing data ingestion and validation

## Common Gotchas
1. **Env vars**: PostgreSQL/MongoDB connections fail silently if env vars unset—defaults: localhost, finnovate DB, admin user
2. **Parquet caching**: `load_processed_parquet()` throws if file doesn't exist—always check or use try/except
3. **Great Expectations context**: Must exist before running validation—initialize with `gx.get_context()`
4. **MLflow tracking**: Runs stored in local `mlruns/` directory—delete to reset experiments
5. **ChromaDB persistence**: Collection names must be unique—use `delete_collection()` to reset

## ADRs (Architectural Decision Records)
- **ADR-001**: Unified Python Stack (Pandas/GX/Scikit-learn/LangChain/Streamlit)
- **ADR-002**: Agent with Structured Tools (Pydantic schemas for deterministic routing)
