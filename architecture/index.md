---
okf_version: "0.2"
---

# Weave Architecture

Weave is a **local-first related-document database**. It loads OKF bundles into memory or a
persistent SQLite index, builds concept nodes and link edges, and answers keyword, BM25 and weighted
fuzzy searches with top-K results. Privacy directives, subprocess extensions, watch reload and an
MCP server are part of the shipped 0.7 surface.

**The UI is retired.** Browser visualization, renderer, mount, lens and Astro are cancelled by
[ADR 0001](adr/0001-keyword-fuzzy-search-and-ui-retirement.md). The Go engine and CLI are the only
product surfaces.

## Purpose

- Load a bundle into memory or a persistent SQLite index.
- Build nodes and edges that relate documents.
- Search by keyword, BM25 lexical ranking and weighted fuzzy matching.
- Navigate the graph with `show`, `backlinks`, `path` and `relate`.
- Audit bundle quality and explain ranking evidence.
- Protect explicitly declared sensitive content.
- Enrich and rerank through optional subprocess extensions.
- Serve the same operations over stdio or TCP MCP.

The detailed contract and algorithms are in
[Keyword + Fuzzy Search](../specs/keyword-fuzzy-search.md).

## Current Topology

```text
┌───────────────────────────────────────────────────────────────┐
│  cmd/weave: CLI, watch loops and `weave mcp` (stdio/TCP)      │
│  argv · envelopes · exit codes · JSONL events                 │
└───────────────────────────────┬───────────────────────────────┘
                                │ operations requests
┌───────────────────────────────▼───────────────────────────────┐
│  engine/operations                                            │
│  ingest · sync · search · audit · relate · explain · export   │
├───────────────────────────────────────────────────────────────┤
│  engine/okf · graph · search · audit · relate · privacy       │
│  parser · edges · FTS5/BM25 · fuzzy · evidence · extensions   │
├───────────────────────────────────────────────────────────────┤
│  storage/sqlite                                               │
│  bundle registry · documents · edges · FTS · postings         │
├───────────────────────────────────────────────────────────────┤
│  contract/v1                                                  │
│  schemas · Go types · envelopes · goldens                     │
└───────────────────────────────────────────────────────────────┘
```

## Layers

| Layer | Language | Package | Responsibility |
| --- | --- | --- | --- |
| Contract | JSON Schema + Go | `contract/v1` | Documents, keywords, search results, envelopes, goldens |
| OKF | Go | `engine/okf` | Parse bundles, frontmatter, links, validation, cache |
| Assets | Go | `engine/assets` | Blob documents, media types and content metadata |
| Graph | Go | `engine/graph` | Nodes, edges, degrees, traversal |
| Audit | Go | `engine/audit` | Conformance, links, index coverage and orphan findings |
| Relate | Go | `engine/relate` | Bounded graph neighborhoods |
| Search | Go | `engine/search` | In-memory catalog, keyword/fuzzy index, BM25 hybrid ranking, explain evidence |
| Privacy | Go | `engine/privacy` | Encryption, tokenization, hashing and key resolution |
| Compression | Go | `engine/compression` | zstd body codec and per-row policy |
| Codecs | Go | `engine/codecs` | Built-in and `weave-codec-<name>` codec resolution |
| Extensions | Go | `engine/extensions` | `weave-<name>` discovery, enrichment and rerank IPC |
| Storage | Go | `storage/sqlite` | Persistent documents, edges, FTS, postings, embeddings/`vec0`, workspace sources and sync |
| Watch | Go | `watch` | Polling snapshots and incremental sync |
| MCP | Go | `mcp` | Tool descriptors, resources and stdio/TCP transport |
| Operations | Go | `engine/operations` | Transport-neutral ingest, rebuild, search (including semantic), navigation, audit, relate and explain requests |
| CLI | Go | `cmd/weave` | Argv, stdout/stderr, envelopes, exit codes and MCP startup |

## Integration Surfaces

| Surface | Audience | Status | Contract |
| --- | --- | --- | --- |
| CLI processes | Any language or runtime | Primary | argv, stdout/stderr, exit codes, `weave.cli/v1` |
| Go package API | Go hosts | Optional | Engine/store packages |
| MCP tool harness | Go hosts, MCP clients | Available | `mcp.Server` + stdio/TCP transport |
| TCP MCP server | MCP clients | Available | newline JSON-RPC over TCP |
| Browser presentation | — | **Retired** | Removed by ADR 0001 |

A host that is not written in Go must use the CLI. A Go host may use the package API, but the CLI
remains the compatibility promise.

## Milestones

| Milestone | Scope | Status |
| --- | --- | --- |
| A — Base engine | contract, parser, graph, operations, machine CLI | Complete |
| B — Search v1 | mandatory keywords, weighted fuzzy search, hybrid top-K, calibration, CLI `search` | Complete |
| C — Cleanup | remove UI, old search and TypeScript implementation; finalize v1 docs | Complete |
| D — Introspection | `weave audit`, `weave relate`, `weave explain` | Complete |
| E — Storage & sync | SQLite persistence, incremental sync, watch | Complete |
| F — Privacy & extensions | Explicit privacy directives and subprocess plugins | Directives, IPC, enrichment, rerank, crypto providers and AI plugin complete |
| G — MCP | MCP tools over operations | Tools, transport, resources, multi-source and sensitive access complete |

## Dependency Rules

1. `contract/v1` has no internal dependencies.
2. `engine/okf` and `engine/graph` may import `contract/v1`; they must not import `search`,
   `operations`, `cmd`, or any UI code.
3. `engine/search` may import `engine/okf`, `engine/graph` and `contract/v1`.
4. `engine/operations` may import the engine, search and navigation packages and `contract/v1`; it
   must not import `cmd`.
5. `cmd/weave` is the only package allowed to read process arguments and environment variables,
   set exit codes, or write output.
6. No package may import Astro, Preact, renderers, mount code or lens assets.
7. The integration boundary is `cmd/weave` plus the operations contract.
8. Every layer boundary is covered by a contract test.

## Key Decisions

| Decision | Choice |
| --- | --- |
| Engine language | Go |
| Product version | 0.7.0 across all products; 1.0.0 is the stability milestone (ADR 0009) |
| Product surface | Go CLI; no UI |
| Document identity | Bundle-relative path minus `.md` |
| Required frontmatter | `type` and `keywords` |
| Keyword search | Exact token + prefix boost; AND semantics |
| Fuzzy fields | Title 1.00, description 0.60, body 0.30 |
| Fuzzy similarity | Normalized Levenshtein and trigram Dice, max |
| Search output | Keyword, fuzzy and hybrid top-K lists |
| Graph neighborhood | 0.7 `weave relate`, bounded BFS depth 0..5 across out/in/both |
| Explainability | 0.7 `weave explain`, keyword/fuzzy/BM25 evidence and hybrid breakdown |
| Ingestion | Strict OKF for parse/graph/search; permissive mode for `ingest`/`rebuild`/`audit` |
| Default mode | Hybrid |
| Default top-K | 10; max 100 |
| Contract version | v1 authoritative; may evolve in place until 1.0.0, then breaking changes need v2 |
| CLI operation | `search` replaces `find` |
| Calibration | Labeled corpus with NDCG@K and MRR@K baselines |
| Storage | Bundle-scoped SQLite default at `~/.weave/index.db`; `--no-db` in-memory; XDG state migration deferred (ADR 0002) |
| Config paths | Platform config dir (`os.UserConfigDir`), platform cache dir, `~/.weave/index.db` for 0.7 |
| Machine output | Additive `weave.cli/v1` schemas, goldens and schema-diff gate |
| Local-first | No telemetry or network by default; `config paths`; network only through opt-in extensions |
| Ranking | Persistent hybrid BM25 + fuzzy; `--no-db` legacy keyword + fuzzy |
| Privacy | 0.7 explicit encrypt/tokenize/hash directives |
| Extensions | 0.7 subprocess IPC over `weave.cli/v1` |
| Blob assets | 0.7 opaque blob documents with `content_metadata`; media semantics stay in extensions |
| Workspaces | 0.7 manifest plus persisted `sources` registry (schema v8) and one index per workspace |
| Scoring | Opt-in `--scorer` extensions reorder a bounded candidate set with a configurable blend; default ranking unchanged |
| Integration | CLI first; Go package optional; MCP tools, transport, resources, multi-source and sensitive access shipped |
| Presentation | Cancelled and removed |

## Documents

| Document | Purpose |
| --- | --- |
| [ADR 0001](adr/0001-keyword-fuzzy-search-and-ui-retirement.md) | New purpose, keywords, fuzzy search and UI retirement |
| [ADR 0002](adr/0002-config-paths-and-db-location.md) | Config/cache/DB paths and additive machine output |
| [ADR 0003](adr/0003-extension-protocol-ownership-and-weave-ai-extraction.md) | `weave-ai` extraction and extension protocol ownership |
| [ADR 0004](adr/0004-generic-blob-assets-and-content-metadata.md) | Generic blob documents, media types and content metadata |
| [ADR 0005](adr/0005-embeddings-and-cgo-free-vec0-index.md) | Durable embeddings, per-space `vec0` indexes and semantic search |
| [ADR 0006](adr/0006-codec-extensions-and-zstd-only-core.md) | zstd-only core, LZ4 as a codec extension and raw-byte codec extensions |
| [ADR 0007](adr/0007-workspace-and-source-registry.md) | Workspace manifest, persisted source registry and single-writer index |
| [ADR 0008](adr/0008-agent-skills-standalone-distribution.md) | Standalone distribution of the agent skills |
| [ADR 0009](adr/0009-product-versioning-0.7-pre-1.0.md) | Product line is 0.7.0; 1.0.0 is the stability milestone |
| [Keyword + Fuzzy Search spec](../specs/keyword-fuzzy-search.md) | Detailed data model, algorithms, CLI and calibration |
| [Contract layer](layers/contract.md) | Documents, keywords, graph and search contract |
| [Engine layer](layers/engine-go.md) | Parser, graph, search and navigation |
| [Operations layer](layers/operations.md) | Transport-neutral requests and envelopes |
| [CLI layer](layers/cli-go.md) | CLI commands, output modes and exit codes |
| [Integration contracts](integration/contracts.md) | CLI, operations and filesystem contracts |
| [Integration steps](integration/steps.md) | Completed search v1 implementation phases |
| [Integration testing](integration/testing.md) | Conformance and test strategy |
| [Weave Audit spec](../specs/weave-audit.md) | Bundle and graph quality gate |
| [Weave Relate spec](../specs/weave-relate.md) | Graph neighborhood command |
| [Weave Explain spec](../specs/weave-explain.md) | Ranking breakdown command |
| [Permissive Ingestion spec](../specs/permissive-ingestion.md) | Markdown-tree ingestion with warnings |
| [Storage & Sync spec](../specs/storage-and-sync.md) | Persistent SQLite, blob metadata and incremental sync |
| [Watch Mode spec](../specs/watch-mode.md) | Live filesystem sync |
| [BM25 Ranking spec](../specs/bm25-ranking.md) | FTS5 lexical ranking |
| [Compression spec](../specs/compression.md) | Text-raw storage, binary zstd and per-row codecs |
| [Codec Extensions spec](../specs/codec-extensions.md) | `weave-codec-<name>` raw-byte codec extensions |
| [Privacy Directives spec](../specs/privacy-directives.md) | Directive parser, keys, storage and search contract |
| [Privacy & Extension Architecture](privacy-and-extensions.md) | Extension IPC and architecture summary |
| [Extension Subprocess IPC spec](../specs/extension-ipc.md) | `weave-<name>` discovery, transport, enrichment, rerank and embeddings |
| [Generic Blob Assets spec](../specs/blob-assets.md) | Opaque blob documents, content metadata and generic retrieval |
| [Weave Image Extension spec](../specs/weave-image.md) | OCR, EXIF and vision enrichment for image blobs |
| [Embeddings spec](../specs/embeddings.md) | Durable embeddings, per-space `vec0` indexes and semantic search |
| [Release Automation spec](../specs/release-automation.md) | Tag-driven verified GitHub Releases |
| [Bundle Export spec](../specs/bundle-export.md) | Raw and encrypted bundle reconstruction |
| [Multiple Bundle Sources spec](../specs/multi-bundle.md) | Aliased multi-root reads and writes |
| [Workspace and Source Registry spec](../specs/workspace.md) | Workspace manifest, persisted source registry and MCP catalog |
| [Extension Data spec](../specs/extension-data.md) | Extension-owned opaque artifacts and retrieval |
| [Pluggable Scoring spec](../specs/extension-scoring.md) | Opt-in scorer extensions, context and blend weights |
| [Optimization spec](../specs/optimization.md) | Benchmarks, budgets and maintainability targets |
| [Performance baseline](performance.md) | Corpus, baselines, budgets and O4/O5 findings |
| [Configuration spec](../specs/configuration.md) | Global YAML config and `WEAVE_*` variables |
| [External Crypto Providers spec](../specs/external-crypto-providers.md) | Age, Vault and KMS provider contract |
| [Weave AI Extension spec](../specs/weave-ai-plugin.md) | Optional enrichment, vision, embeddings and reranking plugin |
| [MCP Server spec](../specs/mcp-server.md) | TCP MCP roadmap and contract |
| [MCP Sensitive Access spec](../specs/mcp-sensitive.md) | Redacted defaults and opt-in decryption |
| [Roadmap](../ROADMAP.md) | Current capabilities and roadmap |

## Reading Order

1. ADR 0001 and this index.
2. Keyword + Fuzzy Search spec.
3. Contract layer.
4. Engine and store/search implementation.
5. Operations and CLI.
6. Integration contracts and testing.
7. ADRs when you need decision context.

## Non-Goals

- Any browser UI, renderer, mount, lens, Astro or Preact work.
- Synonym dictionaries or stemming in the core engine; semantic search uses embeddings as decided in
  [ADR 0005](adr/0005-embeddings-and-cgo-free-vec0-index.md).
- Cross-bundle federated search.
- A query daemon separate from the CLI.
- An HTTP integration API.
- Natural-language question answering.
- Remote multi-tenant MCP hosting.

## Status

The core v1 engine plus `weave audit`, `weave relate`, `weave explain`, SQLite storage, permissive
ingestion, incremental sync and BM25 lexical ranking are implemented. The Go engine parses
mandatory keywords, builds keyword and fuzzy indexes, returns keyword/fuzzy/hybrid top-K results,
exposes the `search` CLI command, audits bundles for conformance and graph quality, returns bounded
graph neighborhoods and explains score components. Bundles are persisted by default in a
bundle-scoped SQLite database at `~/.weave/index.db`; `--no-db` uses the transient parser.
Permissive ingestion synthesizes metadata for dirty Markdown, `weave sync` reconciles changed files
by SHA-256 hash, and persistent hybrid search combines normalized BM25 with fuzzy scores.
Calibration passes its baseline. The UI and old TypeScript stack are removed.

The 0.7 feature set ships in `weave`, `weave-ai`, `weave-codec-lz4`, `weave-image` and
`weave-skills` v0.7.0; see the [release checklist](../release-checklist.md). MCP tools, stdio/TCP
transport, auth, resources and watch reload are available, privacy directives ship with encrypted,
tokenized and hashed storage, bodies use zstd by default, `weave-<name>` extensions enrich writes,
rerank and score searches, blob assets and codec extensions are in place, embeddings back semantic
search, and the schema v8 workspace registry provides `weave workspace`, `weave source` and
`weave mcp --workspace`. Work after 0.7 is watch event delivery (register #40), MCP polish and the
[optimization program](../specs/optimization.md); 1.0 is the stability target.
