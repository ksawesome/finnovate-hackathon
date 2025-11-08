# RAG System Quick Start Guide

## 🚀 Setup (5 minutes)

### 1. Set API Key
```powershell
# Windows PowerShell
$env:GOOGLE_API_KEY='your-gemini-api-key-here'

# Or add to .env file
GOOGLE_API_KEY=your-gemini-api-key-here
```

### 2. Initialize Vector Store (one-time)
```bash
conda activate finnovate-hackathon
python scripts/initialize_rag.py
```

Expected output:
```
✅ RAG System Initialization Complete!
   - 1,358 documents ingested
   - 3 collections created
```

### 3. Validate Installation
```bash
python scripts/quick_validate_rag.py
```

All checks should pass ✅

## 💬 Using the Chat UI

### Start Streamlit App
```bash
streamlit run src/app.py
```

Navigate to: **🤖 AI Assistant** page

### Try These Queries

**Knowledge Base**:
- "What is a trial balance?"
- "Explain variance analysis"
- "What are the SLA deadlines?"

**Account Lookup**:
- "Show me GL account 10010001 for AEML in Mar-24"

**Analytics**:
- "Run variance analysis for AEML"
- "Check SLA compliance"

**Assignments**:
- "What accounts am I assigned to?"

## 🔧 Troubleshooting

### Issue: "GOOGLE_API_KEY not set"
**Solution**: Add API key to .env file or environment variables

### Issue: "No module named 'langchain'"
**Solution**: Run `pip install langchain-google-genai sentence-transformers`

### Issue: "Collection not found"
**Solution**: Run `python scripts/initialize_rag.py --reset`

### Issue: Slow first query
**Solution**: Normal - loading embedding model (~90MB). Subsequent queries are fast.

## 📊 System Components

| Component | File | Purpose |
|-----------|------|---------|
| Document Processor | `src/rag/document_processor.py` | Load & chunk docs |
| Vector Store | `src/rag/vector_store_manager.py` | ChromaDB management |
| RAG Pipeline | `src/rag/rag_pipeline.py` | Gemini integration |
| Agent Tools | `src/langchain_tools.py` | 4 structured tools |
| Chat UI | `src/dashboards/ai_assistant_page.py` | Streamlit interface |

## 📈 Performance

- **Documents**: 1,358 chunks indexed
- **Search**: <500ms latency
- **Accuracy**: 76-98% relevance
- **Tools**: 4 (RAG_Query, GL_Account_Lookup, Analytics, Assignment_Lookup)

## 📚 Documentation

Full documentation: `docs/phases/Phase-2-Part-4-Complete.md` (50+ pages)

---

**Questions?** Check the comprehensive documentation or run `python scripts/quick_validate_rag.py` for diagnostics.
