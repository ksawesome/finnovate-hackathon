# ADR-002: Agent with Structured Tools

## Status

Accepted

## Context

We need reliable tool invocation and deterministic responses for a reporting assistant. Free-form prompts can be brittle; structured tools with typed I/O improve robustness.

## Decision

Use LangChain agent with Pydantic tool schemas and (optionally) model function-calling to route between tools: load/consolidate, validate (GX), variance analytics, review status, insights.

## Consequences

- Pros: Safer tool calls, easier validation, structured outputs that render well in UI and logs.
- Cons: Additional schema work; tool definitions required; slightly higher initial overhead.

## Alternatives considered

- Single prompt “do-everything” chain — harder to validate and test; non-deterministic routing.
