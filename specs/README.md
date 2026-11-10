# Specifications

Every specification owns one behavioral contract. Delivery status lives in the
[roadmap](../ROADMAP.md) and [backlog](../backlog.md); the `Status` column below is document
maturity only.

| Spec | Status | BDD | Register |
| --- | --- | --- | --- |
| [OKF Bundle Parser](okf-bundle-parser.md) | stable | [Node graph](https://github.com/prulloac/weave/blob/main/docs/bdd/node-graph-engine.md) | foundation |
| [Node Graph Engine](node-graph-engine.md) | stable | [Node graph](https://github.com/prulloac/weave/blob/main/docs/bdd/node-graph-engine.md) | foundation |
| [Keyword + Fuzzy Search](keyword-fuzzy-search.md) | stable | — | foundation |
| [Weave Audit](weave-audit.md) | stable | — | 1, 3 |
| [Weave Relate](weave-relate.md) | stable | — | 1, 2 |
| [Weave Explain](weave-explain.md) | stable | [Explain](https://github.com/prulloac/weave/blob/main/docs/bdd/weave-explain.md), [BM25 explain](https://github.com/prulloac/weave/blob/main/docs/bdd/bm25-explain.md) | 1, 4, 21 |
| [Permissive Ingestion](permissive-ingestion.md) | stable | [Permissive ingestion](https://github.com/prulloac/weave/blob/main/docs/bdd/permissive-ingestion.md) | 5 |
| [Storage & Sync](storage-and-sync.md) | stable | [Storage](https://github.com/prulloac/weave/blob/main/docs/bdd/storage-and-sync.md), [Incremental sync](https://github.com/prulloac/weave/blob/main/docs/bdd/incremental-sync.md) | 6, 7 |
| [Watch Mode](watch-mode.md) | stable | [Watch mode](https://github.com/prulloac/weave/blob/main/docs/bdd/watch-mode.md), [Sync watch](https://github.com/prulloac/weave/blob/main/docs/bdd/sync-watch.md) | 8, 24, 40 |
| [BM25 Ranking](bm25-ranking.md) | stable | [BM25](https://github.com/prulloac/weave/blob/main/docs/bdd/bm25-ranking.md), [Calibration](https://github.com/prulloac/weave/blob/main/docs/bdd/bm25-calibration.md) | 9, 10, 21 |
| [Compression](compression.md) | stable | [Compression](https://github.com/prulloac/weave/blob/main/docs/bdd/compression.md), [Codec extensions](https://github.com/prulloac/weave/blob/main/docs/bdd/codec-extensions.md) | 11, 38 |
| [Codec Extensions](codec-extensions.md) | stable | [Codec extensions](https://github.com/prulloac/weave/blob/main/docs/bdd/codec-extensions.md) | 38 |
| [Privacy Directives](privacy-directives.md) | stable | [Privacy](https://github.com/prulloac/weave/blob/main/docs/bdd/privacy-directives.md) | 12 |
| [Extension Subprocess IPC](extension-ipc.md) | stable | [Extension IPC](https://github.com/prulloac/weave/blob/main/docs/bdd/extension-ipc.md) | 13, 14, 15 |
| [External Crypto Providers](external-crypto-providers.md) | stable | [External crypto](https://github.com/prulloac/weave/blob/main/docs/bdd/external-crypto.md) | 17 |
| [Weave AI Extension](weave-ai-plugin.md) | stable | [core behavior](https://github.com/prulloac/weave/blob/main/docs/bdd/ai-plugin.md), [plugin protocol](https://github.com/prulloac/weave-ai/blob/main/docs/bdd/ai-plugin.md) | 16, 34 |
| [MCP Server](mcp-server.md) | stable | [MCP server](https://github.com/prulloac/weave/blob/main/docs/bdd/mcp-server.md), [Transport](https://github.com/prulloac/weave/blob/main/docs/bdd/mcp-transport.md), [Resources](https://github.com/prulloac/weave/blob/main/docs/bdd/mcp-resources.md) | 19, 20, 22, 23, 24 |
| [MCP Sensitive Access](mcp-sensitive.md) | stable | [MCP sensitive](https://github.com/prulloac/weave/blob/main/docs/bdd/mcp-sensitive.md) | 18 |
| [Multiple Bundle Sources](multi-bundle.md) | stable | [Multi-bundle](https://github.com/prulloac/weave/blob/main/docs/bdd/multi-bundle.md), [MCP multi-source](https://github.com/prulloac/weave/blob/main/docs/bdd/mcp-multi-source.md) | 27, 28 |
| [Workspace and Source Registry](workspace.md) | stable | [Workspace](https://github.com/prulloac/weave/blob/main/docs/bdd/workspace.md) | 39 |
| [Release Automation](release-automation.md) | stable | [Release automation](https://github.com/prulloac/weave/blob/main/docs/bdd/release-automation.md) | 25 |
| [Bundle Export](bundle-export.md) | stable | [Bundle export](https://github.com/prulloac/weave/blob/main/docs/bdd/bundle-export.md) | 26 |
| [Configuration](configuration.md) | stable | [Configuration](https://github.com/prulloac/weave/blob/main/docs/bdd/configuration.md), [Machine output](https://github.com/prulloac/weave/blob/main/docs/bdd/machine-output.md), [Help](https://github.com/prulloac/weave/blob/main/docs/bdd/help.md), [Feedback](https://github.com/prulloac/weave/blob/main/docs/bdd/feedback.md), [Onboarding](https://github.com/prulloac/weave/blob/main/docs/bdd/onboarding.md), [Local-first](https://github.com/prulloac/weave/blob/main/docs/bdd/local-first.md), [Error contract](https://github.com/prulloac/weave/blob/main/docs/bdd/error-contract.md), [Dry run](https://github.com/prulloac/weave/blob/main/docs/bdd/dryrun.md) | 30 |
| [Optimization Program](optimization.md) | draft | — | 29 (stretch) |
| [Release Readiness](release-readiness.md) | stable | [Release readiness](https://github.com/prulloac/weave/blob/main/docs/bdd/release-readiness.md) | release gate |
| [1.0 Stability Gate and Issue Policy](stability-gate.md) | stable | — | 41 |
| [Weave Code Extension](weave-code.md) | stable | — | 42 |
| [Pluggable Scoring](extension-scoring.md) | stable | [Scoring](https://github.com/prulloac/weave/blob/main/docs/bdd/extension-scoring.md) | 31 (0.7) |
| [Extension Data API](extension-data.md) | stable | [Extension data](https://github.com/prulloac/weave/blob/main/docs/bdd/extension-data.md) | 32 (0.7) |
| [Generic Blob Assets](blob-assets.md) | stable | [Blob assets](https://github.com/prulloac/weave/blob/main/docs/bdd/blob-assets.md) | 35 |
| [Weave Image Extension](weave-image.md) | stable | [Weave image](https://github.com/prulloac/weave/blob/main/docs/bdd/weave-image.md) | 36 |
| [Embeddings](embeddings.md) | stable | [Embeddings](https://github.com/prulloac/weave/blob/main/docs/bdd/embeddings.md) | 37 |

## Ownership rules

- A spec is owned by the register rows listed above. `foundation` rows predate the register and are
  covered by their behavior tests and calibration baselines.
- `—` means the spec is covered by unit, conformance or calibration tests rather than a separate BDD
  document.
- A spec may be owned by several register rows when the behavior is genuinely shared. The first
  listed spec in a register row owns the contract.
- Behavior scenarios live in [`weave/docs/bdd`](https://github.com/prulloac/weave/blob/main/docs/bdd/README.md);
  decisions live in [`architecture/adr`](../architecture/adr/README.md).
