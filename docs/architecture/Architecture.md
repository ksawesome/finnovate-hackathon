# Project Aura — Architecture

## High-level system diagram

![System Architecture](architecture-detailed.svg)

## Components

### Backend Modules

- **data_ingestion.py**: CSV loading, parsing, PostgreSQL insertion
- **data_validation.py**: Great Expectations suites, MongoDB results storage
- **analytics.py**: SQL queries, aggregations, variance analysis
- **visualizations.py**: Plotly charts, drill-down dashboards
- **insights.py**: Automated insight generation, anomaly detection
- **ml_model.py**: MLflow experiments, model training/serving
- **agent.py**: LangChain agent with function calling
- **langchain_tools.py**: Pydantic tools for structured data access
- **feedback_handler.py**: User feedback collection, model retraining

### Storage Layer (Tri-Store Architecture) - **EXTENDED Phase 0**

**PostgreSQL** - Structured Financial Data (7 Tables, 15+ Indexes)
- **Core Tables:**
  - `users` - Multi-department user management
  - `gl_accounts` (30+ columns) - Complete financial data with company_code, period tracking
  - `responsibility_matrix` (20+ columns) - Multi-stage workflow (Prepare → Review → Final)
  - `review_log` - Audit trail for review actions
- **New Tables (Phase 0):**
  - `master_chart_of_accounts` - 2736 account hierarchy with schedule mapping
  - `gl_account_versions` - JSONB version control for all GL changes
  - `account_master_template` - 2718 historical query templates
- **Capabilities:**
  - Multi-entity support (1,000+ company codes)
  - Multi-period tracking with carryforward balances
  - Full ACID transactions for financial integrity
  - 40+ CRUD operations via `src/db/postgres.py`

**MongoDB** - Semi-Structured Metadata (8 Collections, 25+ Indexes)
- **Core Collections:**
  - `supporting_docs` - Document metadata with nested file arrays
  - `audit_trail` - Event logging with actor tracking (5,000+ events expected)
  - `validation_results` - Great Expectations results with flexible schema
- **New Collections (Phase 0):**
  - `gl_metadata` - Extended descriptions, review notes, tags, historical issues
  - `assignment_details` - Communication logs, status history, escalations
  - `review_sessions` - Workflow state with milestones, checkpoints, blockers
  - `user_feedback` - Observations with resolution tracking, upvotes, priority
  - `query_library` - Standard templates with usage analytics, validation rules
- **Capabilities:**
  - Flexible nested document storage
  - Full-text search on observations and comments
  - Temporal queries on audit trails
  - 30+ helper functions via `src/db/mongodb.py`

**File System** - Unstructured Data
- `data/raw/` - CSV landing zone (original Trial Balance files)
- `data/processed/` - Parquet cache for fast analytics (columnar storage)
- `data/supporting_docs/` - PDF/Excel files organized by GL code and period
- `data/vectors/` - ChromaDB for RAG embeddings (persistent vector store)
- `data/sample/trial_balance_cleaned.csv` - 501 cleaned GL accounts ready for ingestion

**Scale Target:**
- PostgreSQL: 500 MB (2736 accounts × 1000 entities × 12 periods)
- MongoDB: 1 GB (with full audit trail and collaboration data)
- File System: 10 GB (Parquet caches, PDFs, vectors)

See [Storage-Architecture.md](Storage-Architecture.md) and [Data-Storage-Mapping.md](Data-Storage-Mapping.md) for detailed documentation.

## Quality pillars

- CI/CD with lint/type/test/coverage gates.
- Observability: structured logs, timings, error taxonomy.
- Security: bandit, dependency/license checks.
- Performance: caching, vectorized ops, latency budgets.

## Phase mapping

- **Phase 1 (Day 1)**: Data ingestion + PostgreSQL setup + File storage + UI uploaders
- **Phase 2 (Day 2)**: Validation (GX) + MongoDB + Analytics + Basic visualizations
- **Phase 3 (Day 3)**: Feedback handler + ML model + MongoDB audit trails
- **Phase 4 (Day 4)**: LangChain agent + Tools + RAG (ChromaDB) + Advanced UI
- **Phase 5 (Day 5-6)**: Polish, observability, performance tuning, demo hardening

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11
- **Databases**: PostgreSQL 16, MongoDB 7.0
- **Storage**: File system (Parquet, CSV, PDF)
- **Vector Store**: ChromaDB
- **ML**: Scikit-learn, MLflow
- **Agent**: LangChain, OpenAI
- **Data Quality**: Great Expectations
- **Visualization**: Plotly
- **Infrastructure**: Docker Compose
- **CI/CD**: GitHub Actions, pre-commit hooks
