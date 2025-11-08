# Project Aura - Automated Balance Sheet Assurance 🚀

**The Hackstreet Boys submission for 2025 Finnovate Hackathon @ IIT Gandhinagar**

An AI-powered agent for end-to-end financial statement review and validation.

---

## 🎯 Problem Statement

Finance teams across the Adani Group manage 1,000+ legal entities with extensive manual work in reviewing financial statements. Project Aura automates this process using AI agents that:

- ✅ Collect & consolidate data from multiple sources
- ✅ Validate GL accounts with Great Expectations
- ✅ Generate automated reports with insights
- ✅ Provide interactive dashboards & conversational AI
- ✅ Learn from feedback to improve accuracy

---

## 🏗️ Architecture

**Tri-Store Hybrid System:**

- **PostgreSQL**: Structured financial data (GL accounts, users, review logs)
- **MongoDB**: Semi-structured metadata (audit trails, validation results, comments)
- **File System**: Unstructured data (CSVs, PDFs, Parquet cache, vector embeddings)

![System Architecture](docs/architecture-detailed.svg)

See [Architecture.md](docs/Architecture.md) and [Storage-Architecture.md](docs/Storage-Architecture.md) for details.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.11 |
| **Databases** | PostgreSQL 16, MongoDB 7.0 |
| **Storage** | Parquet, ChromaDB |
| **ML** | Scikit-learn, MLflow |
| **Agent** | LangChain, OpenAI |
| **Data Quality** | Great Expectations |
| **Visualization** | Plotly |
| **AI/RAG** | LangChain, Gemini 1.5 Flash, ChromaDB, sentence-transformers |
| **Infrastructure** | Docker Compose |
| **CI/CD** | GitHub Actions, pre-commit |

---

## ✨ Key Features (New in Phase 2!)

### 🤖 AI Assistant with RAG
- **1,358 documents** indexed for semantic search
- **Conversational AI** powered by Gemini 1.5 Flash
- **4 structured tools**: Knowledge base, Account lookup, Analytics, Assignments
- **Dual modes**: Agent (multi-tool) and RAG-only (direct search)
- **Source citations** with relevance scoring
- **<500ms** search latency

Quick start: See [RAG-Quick-Start.md](docs/RAG-Quick-Start.md)

### 📊 Interactive Dashboards
- 5 dashboard types: Overview, Financial, Review, Quality, Risk
- Real-time data from PostgreSQL and MongoDB
- Drill-down capabilities with filters
- Export to CSV/Excel

### 📄 Automated Reports
- Executive summary with hygiene scores
- Variance analysis by entity/period
- SLA compliance tracking
- Multi-period comparison

### 🔄 ML Learning Loop
- Feedback collection UI
- Automated model retraining with MLflow
- Performance tracking and versioning

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Conda (Miniconda or Anaconda)
- Python 3.11+
- Git

### Installation

1. **Clone the repository:**

```powershell
git clone https://github.com/ksawesome/finnovate-hackathon.git
cd finnovate-hackathon
```

2. **Run bootstrap script:**

```powershell
.\scripts\bootstrap.ps1
```

This will:

- Start PostgreSQL & MongoDB containers
- Create conda environment
- Initialize database schemas
- Set up pre-commit hooks
- Create data directories

3. **Activate environment:**

```powershell
conda activate finnovate-hackathon
```

4. **Run the application:**

```powershell
streamlit run src/app.py
```

Open browser to `http://localhost:8501`

---

## 📁 Project Structure

```text
finnovate-hackathon/
├── src/                    # Source code
│   ├── db/                 # Database modules
│   │   ├── __init__.py     # Connection managers
│   │   ├── postgres.py     # SQLAlchemy models
│   │   ├── mongodb.py      # MongoDB operations
│   │   └── storage.py      # File operations
│   ├── data_ingestion.py   # CSV → PostgreSQL pipeline
│   ├── data_validation.py  # Great Expectations
│   ├── analytics.py        # Financial analysis
│   ├── visualizations.py   # Plotly charts
│   ├── insights.py         # Insight generation
│   ├── ml_model.py         # MLflow experiments
│   ├── agent.py            # LangChain agent
│   ├── langchain_tools.py  # Pydantic tools
│   ├── vector_store.py     # ChromaDB RAG
│   ├── feedback_handler.py # User feedback
│   └── app.py              # Streamlit UI
├── data/                   # Data storage
├── docs/                   # Documentation
├── tests/                  # Unit & integration tests
├── scripts/                # Setup scripts
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # Database containers
├── environment.yml         # Conda dependencies
├── Makefile                # Dev commands
└── README.md               # This file
```

---

## 🎮 Usage

### 1. Upload Trial Balance CSV

- Click "Upload CSV" in the sidebar
- Select your trial balance file
- Data is validated and stored in PostgreSQL

### 2. View Dashboard

- See GL account summaries by entity
- Interactive Plotly charts with drill-down
- Pending vs approved review status

### 3. Validate Data

- Click "Validate" button
- Great Expectations runs checks
- Results shown with pass/fail status

### 4. Ask the Chatbot

- Type natural language questions
- "Show me all pending reviews for Adani Ports"
- "What's the variance in Cash account from last month?"
- Agent uses RAG + SQL tools for answers

---

## 🧪 Development

### Pre-commit hooks

First-time setup (one-time):

```powershell
pip install pre-commit
pre-commit install
```

Run on all files:

```powershell
pre-commit run --all-files
```

This runs formatting (black/isort), linting (ruff), type checks (mypy), fast tests, and basic security/secrets scans before commits and on CI.

### Run Tests

```powershell
make test
```

### Lint Code

```powershell
make lint
```

### Format Code

```powershell
make format
```

### Type Check

```powershell
make type-check
```

---

## 🔁 CI/CD

We use GitHub Actions with a multi-job pipeline:

- Pre-commit (runs full pre-commit on PRs)
- Lint & Type Check (ruff, black --check, isort --check-only, mypy --strict)
- Tests (pytest with coverage artifacts)
- Security (bandit, pip-audit)
- CodeQL (static analysis, scheduled weekly)

Release builds (Docker image) publish to GHCR on version tags `vX.Y.Z`.

Create a release:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Image will be available at `ghcr.io/<owner>/<repo>/aura:<tag>`.

---

## 🗄️ Database Access

### PostgreSQL

```powershell
docker exec -it finnovate-postgres psql -U admin -d finnovate
```

### MongoDB

```powershell
docker exec -it finnovate-mongodb mongosh
```

---

## 📚 Documentation

- [Architecture Overview](docs/Architecture.md)
- [Storage Design](docs/Storage-Architecture.md)
- [Test Strategy](docs/Test-Plan.md)
- [6-Day Execution Plan](temp/6-Day-Execution-Plan.md)
- [ADRs](docs/adr/)

### Export docs to PDF (optional)

Requires pandoc (and optionally wkhtmltopdf or xelatex):

```powershell
# Install prerequisites (optional examples)
# choco install pandoc
# choco install wkhtmltopdf

# Export PDFs (Architecture.pdf, Storage-Architecture.pdf, Concept-Note.pdf)
powershell -ExecutionPolicy Bypass -File .\scripts\export-docs.ps1

# Remove old diagram assets to avoid confusion
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup-old-diagrams.ps1
```

---

## 🎯 Roadmap

- **Phase 1 (Day 1)**: File storage + PostgreSQL + CSV ingestion + Basic UI
- **Phase 2 (Day 2)**: GX validation + MongoDB + Analytics + Visualizations
- **Phase 3 (Day 3)**: Feedback + ML model + Audit trails
- **Phase 4 (Day 4)**: LangChain agent + RAG + Advanced UI
- **Phase 5 (Day 5-6)**: Performance + Observability + Demo polish

---

## 👥 Team - The Hackstreet Boys

Built with ❤️ for Finnovate Hackathon 2025 @ IIT Gandhinagar

---

## 📝 License

[MIT License](LICENSE)
