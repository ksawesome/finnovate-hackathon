# ADR-001: Unified Python Stack

## Status

Accepted

## Context

We need to deliver a coherent prototype quickly. A single-language, single-runtime stack minimizes integration friction, accelerates development, and supports a unified data model end-to-end.

## Decision

Adopt a unified Python stack: Pandas (ingestion), Great Expectations (validation), Scikit-learn (learning), LangChain (agent), Streamlit (UI), Plotly (viz).

## Consequences

- Pros: Rapid development, consistent tooling, easy local demo.
- Cons: Less polyglot flexibility; Streamlit vs. BI tools tradeoffs; GPU acceleration optional.

## Alternatives considered

- Power BI + SQL validation + separate chatbot – higher integration overhead, slower iteration.
