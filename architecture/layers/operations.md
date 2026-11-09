---
type: Layer Specification
title: "Operations Layer"
description: "Transport-neutral search, parse, graph and navigation operations shared by the CLI and future transports."
tags:
  - "architecture"
  - "operations"
  - "cli"
  - "mcp"
  - "go"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-10-25T00:00:00Z"
status: draft
---

# Operations Layer

## Purpose

The operations layer defines what Weave can do independently of transport. The CLI and
`weave mcp` both use it without changing engine semantics.

```text
engine/operations
   ↑            ↑
cmd/weave     weave mcp
(CLI)         (stdio/TCP, MCP tools)
```

## Request Model

`contract/v1/types.go` is authoritative; the shape below groups the current fields.

```go
type OperationRequest struct {
    ID, Op, Path, Query            // identity and target
    Mode, TopK, Target             // search and navigation
    From, To, Types, Tags          // path, list filters
    Status, Limit
    FailOn, VerifyKeys, Decrypt    // audit and privacy
    Depth, Direction               // relate
    DB, NoDB, Strict, Permissive   // persistence and ingest mode
    Codec, CodecSet                // body compression
    Assets, NoAssets, AssetTypes   // blob scanning
    Enricher, Embedder, Rerank     // extensions
    Scorer, ScorerWeight, CandidateK // scoring
    TimeoutMS
    Sources                        // multi-source reads and writes
    Out, Format, KeyID, Provider   // export and crypto providers
    Force, Confirmed, DryRun
}
```

Rules:

- `op` is required.
- Bundle operations require `path`; multi-source operations may use `sources` instead.
- `search` requires `query`; `mode` defaults to `hybrid`; `top_k` defaults to 10.
- `--no-db` and `--db` are mutually exclusive.
- Unknown fields are ignored.
- Requests are stateless; a one-shot process may use the parse cache.

## Operation Catalogue

| Op | Required fields | Result |
| --- | --- | --- |
| `contract` | — | `ContractInfo` |
| `parse` | `path` | `Bundle` or `SourceBundles` |
| `graph` | `path` | `Graph` or `SourceGraphs` |
| `search` | `path`, `query` | `SearchResponse` |
| `list` | `path` | `ListResults` |
| `show` | `path`, `target` | `ShowResult` |
| `backlinks` | `path`, `target` | `BacklinksResult` |
| `path` | `path`, `from`, `to` | `PathResult` |
| `version` | — | `VersionInfo` |
| `audit` | `path` | `AuditReport` |
| `relate` | `path`, `target` | `RelateResult` |
| `explain` | `path`, `query` | `ExplainResult` |
| `ingest` | `path` | `IngestReport` |
| `rebuild` | `path` | `IngestReport` |
| `sync` | `path` | `SyncReport` |
| `extensions` | `path` | `ExtensionList` |
| `codecs` | `path` | `CodecList` |
| `export` | `path`, `out`, `format` | `ExportReport` |

`find` is removed. `workspace`, `source`, `embeddings` and `config` are CLI-only command families and
do not have operations descriptors.

## Response Envelope

Success:

```json
{
  "contract": "weave.contract/v1",
  "cli": "weave.cli/v1",
  "ok": true,
  "result": {}
}
```

Failure:

```json
{
  "contract": "weave.contract/v1",
  "cli": "weave.cli/v1",
  "ok": false,
  "error": {
    "code": "CONCEPT_NOT_FOUND",
    "message": "concept not found: missing",
    "details": {"target": "missing"}
  }
}
```

- Exactly one of `result` or `error` is present.
- Error codes are transport-neutral; the CLI maps them to exit codes.
- `search` validation errors (bad mode or top-K) return `INVALID_REQUEST`.

## Volume and One-Shot Behavior

The shipped CLI uses one process per operation. Optional stdio mode remains outside v1.0. The
operations model is stable enough to add it without changing semantics.

## Error Codes

CLI exit classes:

| Exit | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Runtime failure, no match, unknown concept, no route |
| 2 | Usage error, invalid parameters, confirmation required |
| 3 | Permission, privacy key or decryption failure |

`weave contract --json` lists these codes; the owning spec defines when each is returned.

| Code | Class | Owning spec |
| --- | --- | --- |
| `INVALID_REQUEST` | usage | [Keyword + Fuzzy Search](../../specs/keyword-fuzzy-search.md) |
| `INVALID_ROOT` | usage | [Keyword + Fuzzy Search](../../specs/keyword-fuzzy-search.md) |
| `PERMISSION_DENIED` | permission | [Keyword + Fuzzy Search](../../specs/keyword-fuzzy-search.md) |
| `PARSE_ERROR` | runtime | [OKF Bundle Parser](../../specs/okf-bundle-parser.md) |
| `CONCEPT_NOT_FOUND` | runtime | [Keyword + Fuzzy Search](../../specs/keyword-fuzzy-search.md) |
| `PATH_NOT_FOUND` | runtime | [Keyword + Fuzzy Search](../../specs/keyword-fuzzy-search.md) |
| `BUNDLE_NOT_INDEXED` | runtime | [Storage & Sync](../../specs/storage-and-sync.md) |
| `EXTENSION_NOT_FOUND` | usage | [Extension Subprocess IPC](../../specs/extension-ipc.md) |
| `EXTENSION_TIMEOUT` | runtime | [Extension Subprocess IPC](../../specs/extension-ipc.md) |
| `EXTENSION_FAILED` | runtime | [Extension Subprocess IPC](../../specs/extension-ipc.md) |
| `EXTENSION_PROTOCOL` | runtime | [Extension Subprocess IPC](../../specs/extension-ipc.md) |
| `EXTENSION_DATA_INVALID` | runtime | [Extension Data API](../../specs/extension-data.md) |
| `EXTENSION_DATA_TOO_LARGE` | runtime | [Extension Data API](../../specs/extension-data.md) |
| `EXTENSION_DATA_QUOTA` | runtime | [Extension Data API](../../specs/extension-data.md) |
| `EXTENSION_DATA_NOT_FOUND` | runtime | [Extension Data API](../../specs/extension-data.md) |
| `ASSET_TYPES_REQUIRED` | usage | [Generic Blob Assets](../../specs/blob-assets.md) |
| `BLOBS_REQUIRE_DB` | usage | [Generic Blob Assets](../../specs/blob-assets.md) |
| `CODEC_NOT_FOUND` | usage | [Codec Extensions](../../specs/codec-extensions.md) |
| `CODEC_UNAVAILABLE` | runtime | [Codec Extensions](../../specs/codec-extensions.md) |
| `CODEC_FAILED` | runtime | [Codec Extensions](../../specs/codec-extensions.md) |
| `CODEC_TIMEOUT` | runtime | [Codec Extensions](../../specs/codec-extensions.md) |
| `CODEC_PROTOCOL` | runtime | [Codec Extensions](../../specs/codec-extensions.md) |
| `BODY_DECODE_FAILED` | runtime | [Compression](../../specs/compression.md) |
| `PRIVACY_DIRECTIVE_INVALID` | runtime | [Privacy Directives](../../specs/privacy-directives.md) |
| `PRIVACY_KEY_UNAVAILABLE` | permission | [Privacy Directives](../../specs/privacy-directives.md) |
| `PRIVACY_PROVIDER_UNSUPPORTED` | usage | [External Crypto Providers](../../specs/external-crypto-providers.md) |
| `PRIVACY_DECRYPT_FAILED` | permission | [Privacy Directives](../../specs/privacy-directives.md) |
| `CONFIRMATION_REQUIRED` | usage | [Bundle Export](../../specs/bundle-export.md) |
| `INTERNAL` | runtime | — |

## Testing

- Dispatch tests for every operation.
- Search mode/top-K validation tests.
- Envelope success/failure tests.
- CLI process tests reuse the same fixtures.
- Future MCP contract tests reuse the same request/response model.

## Related Documents

- [Contract layer](contract.md)
- [Engine layer](engine-go.md)
- [CLI layer](cli-go.md)
- [Keyword + Fuzzy Search spec](../../specs/keyword-fuzzy-search.md)
- [Integration contracts](../integration/contracts.md)
