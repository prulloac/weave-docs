# Weave Backlog

Tracked work queue for the Weave vision: "To weave flat files into a living universe of knowledge."

**Every tier below ships in the current release line except rows marked `stretch`.** Persistence,
privacy, extensions and MCP are part of the platform, not a later version; the tiers and waves are
internal delivery order.

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
| Extension list short output | [extension-ipc.md](specs/extension-ipc.md) | - | x | x | x | green |
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
| Code knowledge extension | [weave-code.md](specs/weave-code.md) | - | x | x | x | green |

Specification is stable. Slices C1-C5 are implemented and released in v0.8.0: core protocol and
graph relations, eleven-language parsing, cross-file relations, optional symbols and external
documents, traversal, raw export manifests, ignore rules and resource limits. Target: 0.8 / P1.

## Tier 11 — Git sources

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Git source provider | [weave-git.md](specs/weave-git.md) | - | x | x | x | in-progress |

Stable specification. G1–G6 and the G2b/G2c/G5a/G6a follow-ups are implemented: `weave.source/v1`,
manifest source-provider role, schema v9 provenance, stable worktrees, remote fetch with bare
mirrors and offline cache reuse, `_repo` documents, `contains` edges, read-only MCP provenance,
snapshot limits, explicit cache GC, submodule/LFS opt-ins, manifest-backed `Project` /
`ExternalPackage` nodes with `depends_on` edges, opt-in `Commit` history with `parent_of` edges and
deterministic host URLs. The P2 release, integration CI, BDD coverage and schema/`contains`
documentation items are also complete. Released in `weave v0.9.0` and `weave-git v0.9.0`.

Register #43 is shipped in `weave-git` v0.9.0. This tier stays `in-progress` until the open snapshot-diff
follow-up is resolved.

### Git source follow-ups

Open items are listed first; completed items follow under **Done**. Add new items above the Done list
and re-prioritize them when needed.

- [ ] Snapshot diff: `weave-git` compares two revisions (refs or commit-pinned snapshots) and reports
  added, removed and changed documents, with changed relations and frontmatter fields. Core only
  renders the declared output and contains no git logic. Open decision: how a source provider exposes
  a diff request on `weave.source/v1`, since extensions currently expose roles, not subcommands.

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
- [x] Cross-repository integration CI that builds real `weave` and `weave-git` binaries and ingests a
  git source through the workspace flow.
- [x] BDD coverage for remote, workspace, MCP, degraded, auth, security, tags, unknown refs, no-op
  reuse and unsafe paths.
- [x] `contains` documented consistently in the graph specification, architecture layers and ADRs.
- [x] Workspace and storage documentation updated for schema v9 and git provenance.
- [x] G5 manifest discovery: `go.mod`, `package.json`, `Cargo.toml` and `pyproject.toml`.
- [x] `_project` / `_project/<path>` monorepo nodes, `_package/<ecosystem>/<slug>` external package
  nodes and `depends_on` edges with aggregated versions and scopes.
- [x] Manifest description fallback for repositories without a README description.
- [x] G6 opt-in bounded commit history with `Commit` nodes and `parent_of` edges.
- [x] Deterministic `host_kind`, `web_url` and `commit_url` enrichment for GitHub, GitLab,
  Bitbucket and generic remotes without hosting API calls.
- [x] Tagged and published `weave v0.9.0` and `weave-git v0.9.0` with verified archives and checksums.

## Tier 12 — Extension boundaries

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Generic extension output boundary | [extension-output-boundary.md](specs/extension-output-boundary.md) | - | x | x | x | in-progress |

ADR 0012 is accepted and the spec is stable. The generic boundary is implemented end to end;
descriptor-capable `weave-git` and `weave-code` are required. Minimum supported line:
`weave >= 0.11.0`, `weave-git >= 0.11.0`, `weave-code >= 0.11.0`.

### Extension boundary follow-ups

- [x] Accept ADR 0012 and approve the generic extension output boundary spec.
- [x] Write BDD scenarios and link the planned executable coverage.
- [x] Approve the BDD scenarios before writing failing tests.
- [x] Add manifest declarations for document namespaces, artifact namespaces and relation kinds.
- [x] Add generic synthetic document, relation, artifact and source-metadata types.
- [x] Add namespace, relation-kind, path, size and duplicate validation.
- [x] Add the generic source output path and keep the legacy source/project adapters.
- [x] Replace typed source options with opaque `provider_options`; keep CLI flags and typed fields
  as migration sugar.
- [x] Make MCP source provenance expose the generic metadata map.
- [x] Add conformance fixtures proving a non-git provider can add documents and relation kinds.
- [x] Let project analyzers declare document types and content kinds.
- [x] Persist and export generic artifacts; keep the hardcoded `_code`/`_sources` writers during
  migration.
- [x] Move default relation policy into persisted active-extension declarations; reads append them to
  core defaults.
- [ ] Remove the hardcoded `_code`/`_sources` writers after extension producers migrate. Code check
  (2026-11-15): no non-test writer literals remain; the owner should verify and close this item.
- [x] Migrate `weave-git` to descriptors, namespaces, artifacts and `source_metadata`.
- [x] Collect project-analyzer artifacts through the generic storage path.
- [x] Migrate `weave-code` document types and `_code` export to generic descriptors and artifacts.
- [x] Add cross-repository `weave-code` integration for declared types and `_code` artifacts.
- [x] Remove hardcoded `_repo`/`_project`/`_package`/`_commit`/`Code*`/`_code` branches after migration.
- [x] Remove legacy adapters after every first-party conformance and parity suite passes.
- [x] Require descriptor-capable `weave-git`/`weave-code` and record the minimum extension line.

## Tier 13 — Documentation integrity

Drift found in the documentation audit. Each row fixes one inconsistency or gap. Items that change a
spec or an accepted ADR need the usual approval before any `weave` work starts.

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Product version source and cross-document version lint: the git tag is the source (`release.yml` injects it into `weave version`); code stores no version | [ROADMAP.md](ROADMAP.md) | - | - | - | - | review |
| Reconcile the version narrative (ROADMAP headings, backlog "0.7 includes every tier", architecture key decisions); ADR 0009 title stays, since ADRs are immutable | [ROADMAP.md](ROADMAP.md) | - | - | - | - | review |
| Workspace registry schema version: code has v8 (registry), v9 (provider columns) and v10 (extension tables); corrected in the specs and architecture index | [storage-and-sync.md](specs/storage-and-sync.md) | - | - | - | - | review |
| Remove delivery status, milestones and "work after" text from the architecture index; link the roadmap | [architecture/index.md](architecture/index.md) | - | - | - | - | review |
| Reconcile Feature Register and backlog status for #42, #43 and #44 and their tier rows | [ROADMAP.md](ROADMAP.md) | - | - | - | - | review |
| Add a Feature Register row for keyword and fuzzy search, or record the foundation exception in one place | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | - | - | - | review |
| Fix the contradiction in the git follow-ups: the hardcoded `_code`/`_sources` writer item is unchecked while the branch-removal item is checked | [backlog.md](backlog.md) | - | - | - | - | review |
| Replace the duplicated enrichment payloads in the privacy and extensions architecture with a link to the IPC spec | [privacy-and-extensions.md](architecture/privacy-and-extensions.md) | - | - | - | - | review |
| Remove phase-history wording from the extension IPC spec ("This slice", description) | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | review |
| Correct the ROADMAP §2 hybrid row to BM25 + fuzzy for persistent search | [ROADMAP.md](ROADMAP.md) | - | - | - | - | review |
| Confirm the ADR 0002 "v1.0 database location" wording and the policy for fixing typos in accepted ADRs | [ADR 0002](architecture/adr/0002-config-paths-and-db-location.md) | - | - | - | - | review |
| Extend docs checks to cross-validate spec frontmatter, the specs index, the register and the backlog, not only reachability | [STYLE.md](STYLE.md) | - | - | - | - | review |
| Release the 0.11.0 extension line: `weave-git` and `weave-code` descriptor work is on `main` but untagged. The boundary spec minimum is corrected to 0.11.0 and is not satisfied by the released v0.9.0 and v0.8.0 | [extension-output-boundary.md](specs/extension-output-boundary.md) | - | - | - | - | backlog |

## Tier 14 — Extension ergonomics

Makes extension authoring and operation practical without core changes to first-party extensions.

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| **URGENT, resolve ASAP:** selection refusal for `requires` (extension IPC §2.9, ADR 0014). Implemented in `weave` for enrichment, embedding, semantic search, reranking, scoring, project analysis, the `git` source provider and `embed --with-embedder`: manifest fields, `EXTENSION_REQUIREMENT_UNMET` (exit `1`), and BDD tests (`docs/bdd/extension-requirements.md`). Pending review, not merged | [extension-ipc.md](specs/extension-ipc.md) | - | x | x | x | review |
| **URGENT, resolve ASAP:** crypto provider selection (`crypto-<name>`) refuses unmet `requires` and never falls back to the local provider. Implemented in `weave` with a unit test; BDD scenario drafted in `docs/bdd/extension-requirements.md`, awaiting approval. Pending review | [external-crypto-providers.md](specs/external-crypto-providers.md) | - | - | - | - | review |
| Canonical goldens for scorer, embedder, project analysis and source request and response envelopes, with schema definitions and an additive baseline (`weave` repo, `contract/v1`). The `weave-ai` mirror is not updated | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | review |
| Codec conformance check (`weave extensions check codec-<name>`): drafted in codec spec §13 as a proposal, awaiting approval. Requires a decision on canned round-trip input and determinism | [codec-extensions.md](specs/codec-extensions.md) | - | - | - | - | review |
| Codec selection (`--codec <name>`) refuses unmet `requires` with `EXTENSION_REQUIREMENT_UNMET`. Development-build warnings are dropped on storage body paths, which have no warning sink. Pending review | [codec-extensions.md](specs/codec-extensions.md) | - | - | - | - | review |
| `weave extensions check <name>`: validate the manifest and run canned protocol requests (spec §2.8 drafted, awaiting approval) | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| `weave extensions new --role <role> <name>`: scaffold an executable, manifest and fixtures | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Batched request and response envelopes for enrichment and scoring, keeping the single-item form | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Bounded parallel extension invocations with deterministic result order (replaces the sequential rule) | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Role descriptor registry in `engine/extensions`, so a new role touches one adapter instead of many packages | [ADR 0013](architecture/adr/0013-role-descriptor-registry.md) | - | - | - | - | backlog |
| Trust gate for bundle-local `.weave/bin` extensions: opt-in flag or manifest hash allowlist | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Protocol version negotiation: refuse extensions with unmet `requires` at selection (explicit error, no silent fallback), and declare a supported protocol range (spec §2.9 drafted; ADR 0014 proposed) | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Proposal: `weave extensions install <name>` with the staging and requirement checks in §2.10; not scheduled, and whether refusal applies at install is an open decision | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Extension authoring guide for third-party developers in the `weave` repository | [README.md](README.md) | - | - | - | - | backlog |

## Tier 15 — Core features

Proposed core capabilities. Each needs a spec before work starts and a register row when promoted to
the roadmap. Git-specific capabilities such as snapshot diff belong to `weave-git` (Tier 11).

| Feature | Spec | PR | Spec | BDD | TDD | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Per-type frontmatter schemas in `.weave/types/*.yaml`, checked by `weave audit` | - | - | - | - | - | backlog |
| `weave mv` with inbound link rewriting, a changeset and `--dry-run` | - | - | - | - | - | backlog |
| Field filters in `weave search` (for example `type:adr keywords:sqlite`) | [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | - | - | - | - | backlog |
| Graph export formats: `graph --format dot`, `mermaid` and `graphml` | [node-graph-engine.md](specs/node-graph-engine.md) | - | - | - | - | backlog |
| SARIF output for `weave audit` to surface gate failures in code-scanning UIs | [weave-audit.md](specs/weave-audit.md) | - | - | - | - | backlog |
| Enrichment caching by content hash, with `--force` to bypass | [extension-ipc.md](specs/extension-ipc.md) | - | - | - | - | backlog |
| Pluggable tokenizer or analyzer role for language-specific stemming. Needs a decision: it reverses the current non-goal "no synonyms or stemming yet" | [ROADMAP.md](ROADMAP.md) | - | - | - | - | backlog |

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

## Pending Work: Spec, ADR and Dependencies

Classification of every pending row. "Spec" means a new specification or an amendment to an existing
one, which needs explicit approval before `weave` work starts. "ADR" means a new decision record,
numbered from `0013` in the order they are accepted. Items marked "none" are documentation or
migration work that the existing contracts already allow.

### Requirements

| Item | Spec | ADR | Notes |
| --- | --- | --- | --- |
| Tier 5: watch event delivery (`fsnotify`) | amend [watch-mode.md](specs/watch-mode.md) | none | Post-1.0 |
| Tier 11: snapshot diff in `weave-git` | amend [weave-git.md](specs/weave-git.md) and the source protocol | ADR | Adds a new operation to the generic source role, which extends the boundary in ADR 0012 |
| Tier 12: remove hardcoded `_code`/`_sources` writers | none | none | Migration gated by the behavior-preservation rule in ADR 0012 |
| Tier 13: single product version source and lint | none | none | Update [STYLE.md](STYLE.md) |
| Tier 13: reconcile version narrative | none | only if the versioning policy changes | ADR 0009 is accepted and immutable, so a policy change needs a superseding ADR |
| Tier 13: workspace schema version | Correction only (done in this commit) | none | Verified against `storage/sqlite/schema.go` |
| Tier 13: remove delivery status from architecture index | none | none | Documentation only |
| Tier 13: reconcile register and backlog status (#42–#44) | none | none | ROADMAP and backlog only |
| Tier 13: keyword and fuzzy register row | none | none | Could record a foundation exception in STYLE.md |
| Tier 13: backlog `_code`/`_sources` contradiction | none | none | Backlog only |
| Tier 13: privacy and extensions duplicated payloads | none | none | Link to [extension-ipc.md](specs/extension-ipc.md) instead |
| Tier 13: IPC spec phase wording | amend [extension-ipc.md](specs/extension-ipc.md) (wording only) | none | Still needs approval under the spec rules |
| Tier 13: ROADMAP §2 hybrid row | none | none | ROADMAP only |
| Tier 13: ADR 0002 wording and typo policy | none | policy decision; new ADR only if adopted as a rule | ADRs are immutable; errata need a rule |
| Tier 13: extend docs checks | none | none | Tooling and STYLE.md |
| Tier 14: `weave extensions check` | amend [extension-ipc.md](specs/extension-ipc.md) with a conformance section | none | New CLI behavior, so BDD scenarios are needed |
| Tier 14: `weave extensions new --role` | amend [extension-ipc.md](specs/extension-ipc.md) or a new authoring spec | none | New CLI behavior, so BDD scenarios are needed |
| Tier 14: batched envelopes | amend [extension-ipc.md](specs/extension-ipc.md); additive contract change | none | Schema change, so `schema-diff` applies |
| Tier 14: parallel invocations | amend [extension-ipc.md](specs/extension-ipc.md) §2.2 | ADR | Reverses the sequential and deterministic invocation decision |
| Tier 14: role descriptor registry | none | ADR | Extends ADR 0012; no behavior change, so the behavior-preservation gate applies |
| Tier 14: bundle-local trust gate | amend [extension-ipc.md](specs/extension-ipc.md) §2.1 | ADR | Changes a security default that the architecture calls deliberate |
| Tier 14: protocol version negotiation | amend [extension-ipc.md](specs/extension-ipc.md) | ADR | Changes the versioning policy in ROADMAP §9 |
| Tier 14: authoring guide | none | none | End-user guide in `weave/docs/guides`; no BDD |
| Tier 15: per-type frontmatter schemas | new spec | ADR | Changes the Weave profile in invariant 3 |
| Tier 15: `weave mv` with link rewriting | new spec | ADR | Reverses the non-goal "No writes to source bundles" |
| Tier 15: search field filters | amend [keyword-fuzzy-search.md](specs/keyword-fuzzy-search.md) | none | Requires a calibration baseline review |
| Tier 15: graph export formats | amend [node-graph-engine.md](specs/node-graph-engine.md) or a new small spec | none | Additive output |
| Tier 15: SARIF output for audit | amend [weave-audit.md](specs/weave-audit.md) | none | New output format |
| Tier 15: enrichment caching | amend [extension-ipc.md](specs/extension-ipc.md) §2.3 | none | Changes the re-run replacement rule |
| Tier 15: pluggable tokenizer role | new spec | ADR | Reverses the non-goal "No synonyms or stemming yet" and changes ranking, so calibration review applies |

### Dependencies

Arrows read "must come before". Items marked "soft" are preferred but not required.

Documentation integrity:

```text
backlog contradiction ─┐
ROADMAP hybrid row     │
privacy duplication    │
IPC phase wording ─────┼──────────────────────────────┐
                       │                              │
architecture status ───┼─► version narrative ◄─ version source
schema version ────────┘        │                     │
                                │                     │
register/backlog #42–#44 ───────┼─────────────────────┤
keyword register row ───────────┘                     ▼
                                              docs lint extension
```

Feature sequencing:

```text
Tier 12 writer removal ──► role registry ──► batching ──► parallel invocations
                               │   │              ▲
                               │   └─(soft)─► scaffold ──► authoring guide
                               │                  ▲
                               │             extensions check ──┘
                               │                  ▲
                               │       IPC spec wording (D12)
                               │
                               ├──► snapshot diff (also needs source-protocol ADR)
                               └──► tokenizer role (also needs non-goal ADR)

version negotiation ──► batching
version negotiation ──► enrichment caching
trust gate ──► authoring guide
per-type schemas ──(soft)──► SARIF output
mv ──(needs non-goal ADR)
field filters ──(soft)──► tokenizer (both change search evidence; sequence the calibration reviews)
```

Dependency table:

| Item | Depends on | Blocks |
| --- | --- | --- |
| Backlog contradiction | none | Register and backlog reconciliation |
| Architecture status removal | none | Version narrative |
| Schema version correction (done) | none | Version narrative |
| Version source | none | Version narrative, docs lint |
| Version narrative | architecture status removal, schema version, version source, ADR if policy changes | Docs lint |
| Register and backlog reconciliation | backlog contradiction | Docs lint |
| Keyword register row | none | Docs lint, promoting Tier 15 items |
| Docs lint extension | version source, version narrative, reconciliation, keyword register row | Gate for every new spec and register row |
| IPC spec wording | approval | Every IPC spec amendment (avoids conflicting edits) |
| Tier 12 writer removal | none | Role registry, snapshot diff |
| Role registry | Tier 12 writer removal | Batching, parallel invocations, tokenizer role, snapshot diff, scaffold (soft) |
| `extensions check` | IPC spec wording | Scaffold (soft), batching and parallelism tests, authoring guide |
| Scaffold | `extensions check` (soft), role registry (soft) | Authoring guide |
| Version negotiation | IPC spec wording | Batching, enrichment caching |
| Batching | version negotiation, role registry (soft), `extensions check` | Parallel invocations (soft) |
| Parallel invocations | batching (soft), ADR | none |
| Trust gate | IPC spec wording, ADR | Authoring guide |
| Enrichment caching | version negotiation | none |
| Snapshot diff | Tier 12 writer removal, role registry (soft), source-protocol ADR | none |
| Per-type schemas | ADR, contract additive change | SARIF (soft) |
| SARIF output | per-type schemas (soft) | none |
| `weave mv` | non-goal ADR | none |
| Field filters | calibration review | Tokenizer role (soft) |
| Graph export | none | none |
| Tokenizer role | role registry, non-goal ADR, field filters (soft) | none |
| Authoring guide | `extensions check`, scaffold, trust gate | none |
| fsnotify watch | none (post-1.0) | none |

### Sequencing

Documentation integrity comes first. Within the tier:

1. **Now, no approval needed:** backlog contradiction, ROADMAP hybrid row, privacy duplication, architecture
   status removal, schema version resolution, keyword register row, version source, register and backlog
   reconciliation.
2. **Now, needs a decision:** ADR 0002 errata policy, version narrative policy (ADR or not), IPC wording
   approval.
3. **After steps 1–2:** version narrative, then the docs lint extension last, so it checks a consistent
   state.

Features follow the docs work:

1. Tier 12 writer removal, then the role registry, which many later items touch.
2. Decision records for the new ADRs (trust gate, parallel invocations, version negotiation, source
   protocol, non-goal revisions, per-type schema, tokenizer).
3. Specs and BDD for `extensions check`, version negotiation and field filters; then `extensions check`,
   negotiation, field filters, graph export and per-type schemas.
4. Scaffold, batching, enrichment caching, SARIF and snapshot diff.
5. Parallel invocations, the authoring guide, the tokenizer role and fsnotify (post-1.0).

### Release Line

Behavior changes that add capability without changing an existing invocation, file, envelope or
default ship in the 0.X line. A change is breaking only if one of those changes meaning. ROADMAP §9
allows breaking changes in the v1 contract before 1.0 and requires `contract/v2` or `weave.cli/v2`
only after 1.0. Breaking changes ship with release notes.

| Item | Classification | Line |
| --- | --- | --- |
| Batched envelopes | New behavior; single-item form kept | 0.X |
| Parallel invocations | New behavior; result order unchanged | 0.X |
| Trust gate, warn first | New behavior | 0.X |
| Trust gate, default-deny | Breaking for bundles that rely on `.weave/bin` | Decision needed; 0.X only as opt-in |
| Version negotiation, refusal | Breaking for installs running extensions with unmet requirements; decided by the owner, recorded in ADR 0014 | 0.X, with release notes |
| Enrichment caching | New behavior; opt-in or bypassed with `--force` | 0.X |
| Per-type schemas (opt-in config) | New behavior | 0.X |
| `weave mv` | New command | 0.X |
| Search field filters | Additive flags | 0.X |
| Graph export formats | Additive output | 0.X |
| SARIF output | Additive output | 0.X |
| Tokenizer role | New opt-in role; default ranking unchanged | 0.X |
| Snapshot diff | New capability in `weave-git` | 0.X |
| fsnotify watch events | New non-breaking behavior | 0.X eligible; the register says post-1.0, so that row needs an edit if confirmed |

Feature work does not reset the 1.0 gate. Only confirmed defects do: a fix on `main` restarts the
30-day window, and the earliest 1.0.0 date is 2026-12-10.

### Drift Analysis (2026-11-15)

Checked against the code, tags and migrations before any item was started:

- **Schema:** `storage/sqlite/schema.go` sets `schemaVersion = 10`. v8 creates the `sources` registry,
  v9 adds `provider` and `metadata_json`, and v10 adds `extension_artifacts` and
  `extension_relations`. Three specs and the architecture index named v10 for the registry; they are
  corrected in this commit.
- **Product version:** no version is stored in code. `release.yml` injects the git tag into
  `weave version` with `-X main.version`. The latest tag is `v0.10.1`. Remaining drift is listed in the
  Tier 13 version rows: ADR 0009, architecture key decisions, the ROADMAP §2 and §3 headings and the
  backlog's "0.7 includes every tier".
- **Extension line:** `weave-git` is tagged `v0.9.0` and `weave-code` `v0.8.0`, but both have
  descriptor work on `main` that is not tagged. The generic boundary spec requires `>= 0.11.0` for both,
  which no tag provides. ROADMAP #44 calls the boundary shipped, so the claim holds on `main` only.
- **Legacy writers:** no non-test code writes `_code`, `_sources`, `_repo`, `_project`, `_package` or
  `_commit` literals. The only `_repo` in non-test code is a comment in `engine/operations/write.go`.
  The unchecked Tier 12 item appears complete; the owner should verify and close it.
- **Pending features, verified absent:** per-type schemas (no `.weave/types` reference), `extensions
  check` and `extensions new` (no subcommand), SARIF, `weave mv`, a `graph --format` flag (only `export`
  has `--format`), enrichment caching and a tokenizer or stemming path. Search has no type or tag filters;
  `list` has them (`cmd/weave/flags.go`).
- **Matches the docs:** `.weave/bin` is searched before `PATH` and the first match wins (`discoverDir`),
  the default timeout is 5 seconds, and the enrichment request carries `doc_path` and `bundle_root`.
  No goroutines in `engine/extensions`, so invocations are sequential as the spec states.

## Maintenance

Keep this file updated as pipeline phases advance. Checkboxes in the phase columns are toggled per feature as they complete.
