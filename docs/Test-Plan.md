# Project Aura — Test Plan

## Scope

Covers unit, integration, end-to-end, data validation, property-based, performance, and acceptance testing for the hackathon deliverable.

## Quality gates

- Lint: ruff+black+isort clean
- Types: mypy (strict) with zero errors
- Tests: pytest pass with coverage ≥ 80%
- Data validation: GX checkpoints pass on golden datasets
- Performance: p95 latency under 800ms for key operations (ingestion, validation, variance)

## Test levels

### Unit tests

- src/data_ingestion.py: schema enforcement, consolidation joins
- src/data_validation.py: expectation suite creation, checkpoint execution (mocked context)
- src/analytics.py: variance, review status, SLA deviation, hygiene metrics
- src/ml_model.py: training, save/load, prediction
- src/feedback_handler.py: logging, merge, dedupe
- src/langchain_tools.py: tool I/O contracts and error handling

### Property-based tests

- Ingestion functions with randomized CSVs (hypothesis) — ensure invariants (no nulls in key cols)
- Variance function monotonicity and bounds

### Integration tests

- Pipeline: upload → ingest → validate (GX) → analytics → visual artifacts generated
- Learning loop: feedback → retrain → improved metric vs baseline (on fixture dataset)
- Agent tools: tool orchestration calling analytics/validation and returning structured output

### End-to-end tests

- Streamlit app (Playwright or streamlit-testing):
  - Upload fixtures, run validation, view charts, perform correction, retrain, ask agent query
  - Assertions on visible text, charts rendered, and status badges

### Data validation tests (Great Expectations)

- Expectation suite: debit=sum(credit), non-null critical columns, allowed types
- Custom expectations for SLA and hygiene calculations
- Data Docs generation and checkpoint runs on golden datasets

### Performance tests

- Benchmark ingestion, validation, and analytics on small/medium/large CSVs
- Cache effectiveness: repeated runs show improved timings
- Memory profiling for worst-case datasets

### Security & resilience

- Bandit scan clean
- Dependency and license audit clean
- Offline demo runbook works; app remains operable without internet

### Acceptance criteria mapping

- All problem statement capabilities demonstrated
- Evidence of learning: correction improves model accuracy
- Conversational interface answers key queries; proactive insights displayed
- Dashboards provide drill-down, status, and hygiene indicators
