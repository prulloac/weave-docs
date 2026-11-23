---
type: Architecture Decision Record
title: "ADR 0016: Opt-In Parallel Extension Invocation"
description: "Keeps extension invocation sequential by default and adds an explicit per-command concurrency bound, with results merged in request order so output stays deterministic."
tags:
  - "architecture"
  - "extensions"
  - "concurrency"
  - "ipc"
status: accepted
---

# ADR 0016: Opt-In Parallel Extension Invocation

## Context

[Extension Subprocess IPC §2.2](../../specs/extension-ipc.md) runs one request per process and invokes
extensions sequentially. That keeps output deterministic and avoids shared state, but a batch or a
large ingest pays the full latency of each extension call in series. Batched envelopes
([§2.2](../../specs/extension-ipc.md)) remove process startup per document; they do not, by
themselves, overlap provider latency. The owner asked for batching first and parallelism only as an
explicit choice, not a new default.

## Decision

1. **Sequential remains the default.** One invocation at a time unless the caller sets
   `--extension-parallelism N`.
2. **One bound per command.** `N` is `1` by default and accepts `1` through `8`; values outside that
   range are `INVALID_REQUEST`, exit `2`. The bound applies to the whole command, not to each
   extension separately, because a command selects at most one extension per role today.
3. **Ordered results.** Inputs keep their order. Responses, merged keywords, added warnings and
   extension-data writes are applied in input order after all invocations settle, so the observable
   output is identical to the sequential run with the same inputs.
4. **No shared process state.** Each request still gets its own process, stdin, stdout, stderr and
   timeout. There is no long-lived worker, connection pool or extension-managed queue.
5. **Failure isolation.** A failed item is handled exactly as in the sequential path: enrichment
   warnings keep core results, rerank and scoring fall back, and a source write fails. One failure
   does not cancel in-flight items; it is reported in the item's position.
6. **No retries.** Parallelism is not a retry policy. A failed invocation is not repeated.
7. **Transport scope.** The bound covers batch items and the per-document enrichment loop. Commands
   that invoke exactly one extension once (rerank, scorer, a single source materialization) see no
   change. MCP inherits sequential behavior in the first release because it has no per-call flag.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Default to `4` | Rejected: it changes behavior and resource use without the user asking |
| Manifest-declared `max_concurrency` | Deferred: a manifest could then raise core's resource use; the flag stays authoritative |
| Per-role flags (`--enrich-parallelism`, etc.) | Rejected for now: one bound is simpler and covers the only multi-item roles |
| Long-lived worker processes | Rejected: it reverses the one-request-per-process isolation in §2.2 |
| Parallel by default with `--extension-parallelism 1` to opt out | Rejected: determinism and provider rate limits are safer as opt-in |

## Consequences

- Large ingests and batches can overlap provider latency without changing output.
- Providers see concurrent requests only when the user asks, which matters for rate limits and local
  models.
- Tests must assert byte-identical output for `N=1` and `N=8`, including warning and keyword order.
- A future manifest cap can be added additively; it cannot weaken the `1..8` flag bound.
