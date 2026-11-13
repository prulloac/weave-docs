# Weave Backlog

Tracked work queue for the Weave vision: "To weave flat files into a living universe of knowledge."

**0.7 includes every tier below except rows marked `stretch`.** Persistence, privacy, extensions and
MCP are 0.7 scope, not a later platform; the tiers and waves are internal delivery order.

Status legend:

- `backlog` — not started
- `in-progress` — actively worked
- `red` — tests written, failing (BDD/TDD phase)
- `green` — tests passing
- `review` — PR submitted, awaiting review/merge
- `done` — merged
- `stretch` — post-1.0; tracked but not a 0.7 gate

Pipeline phase legend (per SDD -> BDD -> TDD):

- `-` — not applicable / not started
- `x` — complete

## Tier 1 — Foundation

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OKF Bundle Parser | [okf-bundle-parser.md](specs/okf-bundle-parser.md) | [#1](https://github.com/prulloac/weave/pull/1) | x | x | x | done |

## Tier 2 — Engine

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Node Graph Engine | [node-graph-engine.md](specs/node-graph-engine.md) | - | x | x | x | green |
| Keyword + Fuzzy Search (core v1) | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | x | x | x | green |
| Weave CLI Search & Navigate | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | x | x | x | green |

## Tier 3 — Search core

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Mandatory keywords, fuzzy scoring, hybrid top-K and calibration | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | x | x | x | green |
| Remove `find`; add `weave search` | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | x | x | x | green |
| Calibration corpus and ranking baselines | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | x | x | x | green |
| `weave audit` bundle quality gate | [weave-audit.md](specs/weave-audit.md) | - | x | x | x | green |
| `weave relate` graph neighborhood | [weave-relate.md](specs/weave-relate.md) | - | x | x | x | green |
| `weave explain` ranking breakdown | [weave-explain.md](specs/weave-explain.md) | - | x | x | x | green |
| Introspection contract types (audit/relate/explain) | [weave-audit.md](specs/weave-audit.md) | - | x | x | x | green |

## Tier 4 — Portability

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Go engine + CLI base | [architecture/index.md](architecture/index.md) | - | x | - | - | done |
| Roadmap: current capabilities and 0.7 scope | [ROADMAP.md](ROADMAP.md) | - | x | - | - | done |

## Tier 5 — 0.7 Platform

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Persistent SQLite storage | [storage-and-sync.md](specs/storage-and-sync.md) | - | x | x | x | green |
| Incremental sync | [storage-and-sync.md](specs/storage-and-sync.md) | - | x | x | x | green |
| Watch mode | [watch-mode.md](specs/watch-mode.md) | - | x | x | x | green |
| Watch event delivery (`fsnotify`) | [watch-mode.md](specs/watch-mode.md) | - | - | - | - | backlog |
| Permissive Markdown ingestion | [permissive-ingestion.md](specs/permissive-ingestion.md) | - | x | x | x | green |
| BM25 lexical ranking | [bm25-ranking.md](specs/bm25-ranking.md) | - | x | x | x | green |
| BM25 calibration | [bm25-ranking.md](specs/bm25-ranking.md) | - | x | x | x | green |
| BM25 explain evidence | [bm25-ranking.md](specs/bm25-ranking.md) | - | x | x | x | green |
| Memory/body compression | [compression.md](specs/compression.md) | - | x | x | x | green |
| Privacy directives | [privacy-directives.md](specs/privacy-directives.md) | - | x | x | x | green |
| External crypto providers | [external-crypto-providers.md](specs/external-crypto-providers.md) | - | x | x | x | green |
| Extension subprocess IPC | [extension-ipc.md](specs/extension-ipc.md) | - | x | x | x | green |
| Enrichment extension | [extension-ipc.md](specs/extension-ipc.md) | - | x | x | x | green |
| Rerank extension | [extension-ipc.md](specs/extension-ipc.md) | - | x | x | x | green |
| AI enrichment/reranking plugin | [weave-ai-plugin.md](specs/weave-ai-plugin.md) | - | x | x | x | green |

## Tier 6 — MCP

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MCP in-memory over operations | [mcp-server.md](specs/mcp-server.md) | - | x | x | x | green |
| MCP persistent binding | [mcp-server.md](specs/mcp-server.md) | - | x | x | x | green |
| MCP watch reload | [watch-mode.md](specs/watch-mode.md), [mcp-server.md](specs/mcp-server.md) | - | x | x | x | green |
| MCP stdio/TCP transport | [mcp-server.md](specs/mcp-server.md) | - | x | x | x | green |
| MCP resources | [mcp-server.md](specs/mcp-server.md) | - | x | x | x | green |
| Sensitive MCP access policies | [mcp-sensitive.md](specs/mcp-sensitive.md) | - | x | x | x | green |
| MCP multiple sources | [multi-bundle.md](specs/multi-bundle.md) | - | x | x | x | green |

## Tier 7 — Delivery, portability and quality

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Release automation | [release-automation.md](specs/release-automation.md) | - | x | x | x | green |
| User-level installers | [release-automation.md](specs/release-automation.md) | - | x | - | x | green |
| Bundle export (raw/encrypted) | [bundle-export.md](specs/bundle-export.md) | - | x | x | x | green |
| Multiple bundle sources | [multi-bundle.md](specs/multi-bundle.md) | - | x | x | x | green |
| Performance and maintainability | [optimization.md](specs/optimization.md) | - | x | x | x | stretch |
| Global configuration | [configuration.md](specs/configuration.md) | - | x | x | x | green |
| Release readiness (regression, smoke, docs) | [release-readiness.md](specs/release-readiness.md) | - | x | x | x | green |
| Pluggable scoring | [extension-scoring.md](specs/extension-scoring.md) | [#17](https://github.com/prulloac/weave/pull/17) | x | x | x | green |
| Extension data API | [extension-data.md](specs/extension-data.md) | [#15](https://github.com/prulloac/weave/pull/15) | x | x | x | green |
| weave-ai extraction and IPC conformance | [ADR 0003](architecture/adr/0003-extension-protocol-ownership-and-weave-ai-extraction.md), [weave-ai-plugin.md](specs/weave-ai-plugin.md) | - | x | x | x | green |
| AI vision and embeddings | [weave-ai-plugin.md](specs/weave-ai-plugin.md) | - | x | x | x | green |
| Generic blob assets | [blob-assets.md](specs/blob-assets.md) | - | x | x | x | green |
| Image knowledge extension | [weave-image.md](specs/weave-image.md) | - | x | x | x | green |
| Embeddings and semantic search | [embeddings.md](specs/embeddings.md) | - | x | x | x | green |
| Codec extensions | [codec-extensions.md](specs/codec-extensions.md) | - | x | x | x | green |

User-level installers: `v0.7.0` published for `weave`, `weave-ai`, `weave-codec-lz4`, `weave-image`
and `weave-skills`; Unix and PowerShell installers verified against the release assets.

ADR 0003 is accepted. `weave-ai` is standalone in `prulloac/weave-ai`; `cmd/weave-ai` is removed
from `weave`, and conformance tests cover both sides. The `v0.7.0` release is published.

Media and embeddings: ADR 0004/0005/0006 are accepted and the specs/BDD are approved (2026-11-03).
`weave-ai` vision/embeddings are green. Core schema v7, blob ingestion/retrieval, codec extensions
and the embedding ingest/search/audit/list/rebuild/drop path are implemented and covered by tests.
`weave-codec-lz4` and `weave-image` exist as standalone extension repositories with installers, CI
and release workflows. `weave`, `weave-ai`, `weave-codec-lz4`, `weave-image` and `weave-skills`
v0.7.0 are published; see [release-checklist.md](release-checklist.md).

`v0.8.0` is published for `weave`, `weave-ai`, `weave-code`, `weave-codec-lz4`, `weave-image` and
`weave-skills`, including the code knowledge feature. See
[release-checklist.md](release-checklist.md).

0.7 pluggable scoring: spec and BDD approved; search and explain CLI slices merged in PR #17.
0.7 extension data: spec and BDD approved; E1 (manifest, schema v6 and
transactional import), E2 (CLI list/get/gc), E3 (show refs, MCP blob
resources) and E4 (raw export, encrypted-export policy) are merged in PR #15 and released in
v0.7.0.

## Tier 8 — Workspace and sources

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Workspace and source registry | [workspace.md](specs/workspace.md) | - | x | x | x | green |

Workspace and sources: ADR 0007 and the
[Workspace and Source Registry specification](specs/workspace.md) are accepted (2026-11-06). The
schema v8 registry, `weave workspace`/`weave source` commands, `ingest|rebuild|sync --workspace`,
`weave mcp --workspace` with the `weave_sources` tool, runtime re-reconciliation and the
single-writer index lock are implemented, merged on `main` and released in v0.7.0.

## Tier 9 — Stability and community

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1.0 stability gate and issue policy | [stability-gate.md](specs/stability-gate.md) | - | x | - | - | green |

Gate: 1.0.0 opens after 30 consecutive days without a declared defect, with no open
`confirmed-defect` issue in `prulloac/weave`. The current window started on 2026-11-10. Only
`prulloac/weave` accepts issues; the other repositories are closed and link here.

## Tier 10 — Code knowledge

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Code knowledge extension | [weave-code.md](specs/weave-code.md) | - | x | x | x | review |

Specification is stable. Slices C1-C5 are implemented and released in v0.8.0: core protocol and
graph relations, eleven-language parsing, cross-file relations, optional symbols and external
documents, traversal, raw export manifests, ignore rules and resource limits. Target: 0.8 / P1.

## Tier 11 — Git sources

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Git source provider | [weave-git.md](specs/weave-git.md) | - | x | x | x | in-progress |

Stable specification. G1–G4 are implemented: `weave.source/v1`, manifest source-provider role,
schema v9 provenance, stable worktrees, remote fetch with bare mirrors and offline cache reuse,
`_repo` documents, `contains` edges, read-only MCP provenance, snapshot limits, explicit cache GC
and submodule/LFS opt-ins. Next: cross-repository integration CI and the remaining P2 documentation
and coverage items. Target: 0.9 / P1.

### Git source follow-ups

Living checklist. Add new git-source items here, re-prioritize them, and mark `[x]` when merged. Keep
this section until every item is checked.

**P0 — local usability and correctness**

All local P0 items are complete.

**P1 — next feature slices**

All P1 feature slices are complete.

**P2 — release and coverage**

- [ ] Add cross-repository integration CI using real `weave` and `weave-git` binaries.
- [ ] Complete BDD coverage for remote, workspace, MCP, degraded, auth and security scenarios.
- [ ] Document `contains` consistently in graph specifications and ADRs.
- [ ] Update workspace and storage docs for schema v9.

**Done**

- [x] Source-provider contract, manifest role and stable source IDs.
- [x] Local `weave-git` provider with stable worktrees and commit pinning.
- [x] CLI `--git`, `--ref` and `--worktree` local ingestion.
- [x] `_repo` repository document and `contains` edges.
- [x] Schema v9 source registry columns.
- [x] Original path/URI to snapshot read mapping.
- [x] Source-provider warning propagation into ingest and sync reports.
- [x] README frontmatter description extraction.
- [x] `weave.source/v1` request and provider capability validation.
- [x] Synthetic `_repo` export under `_sources/repositories.json`.
- [x] Workspace `git:` / `ref:` object sources, `source add --git` and workspace-scoped source IDs.
- [x] Git provenance persistence and `source list/show` provider, URI, ref and commit output.
- [x] Permissive provider failures degrade only the failed source and preserve its previous snapshot.
- [x] Remote git fetch for HTTPS, SSH, SCP-like and `file://` URIs, shallow depth hints and offline
  cached-commit reuse.
- [x] Documented the system `git` backend; pure-Go `go-git` remains deferred.
- [x] MCP `weave_sources` and `weave://workspace/sources` serve snapshot paths plus provider, URI,
  ref and commit provenance without fetching.
- [x] Snapshot size, file, project and file-count limits with safe failure before the worktree swap.
- [x] Explicit `weave-git gc` for stale staging trees, incomplete source caches and mirror pruning.
- [x] Submodule and Git LFS opt-ins with archive-safe defaults and `.git` stripping.
- [x] `weave-git` tag-driven release workflow, six static archives, checksums, draft release and
  user-level installers.

## Cross-cutting

- [x] Knowledge corpus: vision + related concepts (`knowledge/`)
- [x] okf-generator skill aligned to OKF v0.2
- [x] spec-writer skill actor convention aligned to OKF v0.2
- [x] Go test infrastructure: unit, conformance, calibration, CLI process tests
- [x] CI workflow: contract export diff, `go test -race`, vet, gofmt, build, docs lint
- [x] `scripts/verify.sh` full local gate
- [x] Qualitative optimization: config paths/provenance and additive machine output
- [x] Maintainability: shared CLI harness, table-driven dispatch and one error table per boundary
- [x] Feedback and onboarding: quiet/verbose/progress/ASCII, start screen, empty states, completion
- [x] Local-first trust: no-telemetry statement, `config paths`, extension search paths
- [x] Benchmarks: deterministic corpus, registry, package benchmarks, `cmd/bench`, baseline and advisory CI
- [x] O4 slices: metadata keyword search, lazy/slim index, persistent fuzzy/hybrid/explain evidence, vocabulary prefilter and incremental sync
- [x] Documentation integrity: indexes, contiguous numbering, one status source and `cmd/docs-lint` rules
- [x] Built-binary smoke suite: CLI, sync, export, privacy, multi-source and MCP stdio
- [x] Regression hardening: shuffled race suite, injected progress timing and parser fuzz targets
- [x] License: MIT, included in release archives
- [x] CONTRIBUTING.md: development process, worktrees, stacked PRs, PR template
- [x] PR template: `.github/PULL_REQUEST_TEMPLATE.md`
- [x] Contract v1 schemas, generated types, golden corpus and exporter (Phase 0)
- [x] Go module scaffold, contract structs, schema round-trip tests and CI (Phase 2)
- [x] Go engine port: parser, graph, search, navigation and operations (Phase 3)
- [x] Go machine CLI: commands, envelopes, exit codes and cache defaults (Phase 5A / Milestone A)
- [x] ADR 0001: keyword + fuzzy search
- [x] Keyword + Fuzzy Search specification
- [x] Search calibration corpus and baseline report
- [x] 0.7 storage/sync and privacy/extension specifications placed under `specs/`
- [x] Extended roadmap integrated into `ROADMAP.md`
- [x] Audit contract, engine and CLI behavior suite (`weave audit`)
- [x] Relate contract, engine and CLI behavior suite (`weave relate`)
- [x] Explain contract, search evidence and CLI behavior suite (`weave explain`)
- [x] SQLite storage foundation: default bundle-scoped DB, ingest, rebuild, `--db`/`--no-db`
- [x] Permissive ingestion: synthetic documents, warnings, permissive audit and search inclusion
- [x] Incremental sync: hash skip, add/update/remove/rename, cascade and mode persistence
- [x] BM25 lexical ranking: FTS indexing, multi-token OR, phrases, negative terms and field weights
- [x] BM25 calibration: BM25 + fuzzy hybrid corpus, baselines and deterministic metrics
- [x] BM25 explain: lexical raw/normalized scores, matched fields and term contributions
- [x] MCP M1: in-process tool descriptors, dispatch, validation and error mapping
- [x] MCP transport: stdio/TCP newline JSON-RPC, initialize, tools and token auth
- [x] MCP resources: bundle index/stats and concept/neighborhood templates
- [x] Watch reload: polling sync loop, MCP live updates and clean shutdown
- [x] Privacy directives: encrypt/tokenize/hash, key resolution, redaction and alias search
- [x] Extensions: discovery, `weave.cli/v1` runner, enrichment keywords and rerank blending
- [x] Release automation: tag-driven verified builds, archives, checksums and draft releases
- [x] Multiple bundle sources: repeatable `--source`, merged search/list/audit and multi-source writes
- [x] MCP multiple sources: sourced tools, qualified targets and `weave://source/<alias>/...` resources
- [x] MCP sensitive access: redacted defaults, opt-in decryption and audit key checks
- [x] AI plugin: `weave-ai` with Ollama/OpenAI/Gemini providers, redaction and opt-in
- [x] Sync watch CLI: `weave sync --watch` with JSONL events and clean shutdown
- [x] Bundle export: raw plaintext with confirmation and re-ingestable encrypted export
- [x] External crypto providers: `weave-crypto-<name>` selection, IPC, key versions and audit
- [x] Global configuration: YAML file, `WEAVE_*` variables, `config show|path|init`
- [x] Body compression: per-row codec and decode recovery; 0.7 uses text raw, binary zstd and
  extension-provided LZ4/other codecs

## Dependency Order

The full feature DAG lives in [ROADMAP.md § Feature Dependency Map](ROADMAP.md#feature-dependency-map).
The authoritative feature-to-spec mapping is
[ROADMAP.md § Feature Register](ROADMAP.md#feature-register); every undelivered feature must have
one row here and one row there.

Execution waves:

1. Shipped: parser, graph, search, CLI, calibration.
2. Parallel: introspection contract types (done), `audit` (done), `relate` (done), `explain` (done), permissive ingestion (done).
3. Storage: SQLite (done).
4. Parallel: sync (done), BM25 (done), BM25 calibration (done), BM25 explain (done), MCP in-memory (done), MCP persistent (done).
5. Watch (done) and privacy directives (done).
6. Extension runner, enrichment and rerank (done); sensitive MCP (done).
7. AI plugin (done), external crypto (done).
8. Release automation (done), bundle export (done), multiple bundle sources (done).
9. Release readiness: documentation integrity, regression hardening and the built-binary smoke suite.
10. 0.7: pluggable scoring extensions with document context and configurable blend weights (done).
11. Stretch: maintainability and UX follow-ups, benchmarks, time and space.
12. Post-1.0: `fsnotify` watch event delivery with a polling fallback.
13. 1.0 gate: 30 consecutive days without a declared defect; only `weave` accepts issues.
14. 0.8 / P1: `weave-code` project analysis, code relations and optional symbol documents.

Critical path: `contract -> parser/graph/search -> storage -> sync -> BM25 -> privacy -> extension runner -> MCP sensitive`.

## Maintenance

Keep this file updated as pipeline phases advance. Checkboxes in the phase columns are toggled per feature as they complete.
