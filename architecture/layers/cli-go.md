---
type: Layer Specification
title: "CLI Layer (Go)"
description: "Primary integration contract for search, parse, graph and navigation: envelopes, stdout/stderr, exit codes and top-K search flags."
tags:
  - "architecture"
  - "cli"
  - "go"
  - "integration"
  - "search"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-10-25T00:00:00Z"
status: draft
---

# CLI Layer (Go)

## Purpose

`cmd/weave` is the primary integration surface. It adapts argv/stdin/stdout to
[operations](operations.md) and owns:

- argument parsing,
- environment resolution,
- human and machine output,
- stdout/stderr separation,
- exit codes.

There is **no presentation command**. `mount`, `unmount`, `status`, `find` and `--legacy-json`
are gone or deferred.

## Command Surface

```sh
weave contract [--json]
weave parse <path> [--source <alias=path>] [--json] [--no-cache]
weave graph <path> [--source <alias=path>] [--json] [--no-cache]
weave search <path> <query> [--mode hybrid|keyword|fuzzy|bm25|semantic] [--top-k <n>] [--embedder <name>] [--rerank <name>] [--scorer <name>] [--scorer-weight <0..1>] [--candidate-k <n>] [--json] [--no-cache]
weave list <path> [--type <t>] [--tag <t>] [--status <s>] [--limit <n>] [--json]
weave show <path> <id|file> [--out <file>] [--decrypt] [--provider <name>] [--json]
weave backlinks <path> <id|file> [--json]
weave path <path> <id|file> <id|file> [--json]
weave audit <path> [--fail-on error|warning|none] [--verify-keys] [--provider <name>] [--json]
weave relate <path> <id|file> [--depth <n>] [--direction out|in|both] [--json]
weave explain <path> <query> [--id <id>] [--mode hybrid|keyword|fuzzy|bm25] [--top-k <n>] [--scorer <name>] [--scorer-weight <0..1>] [--candidate-k <n>] [--json]
weave ingest <path>|--workspace <dir> [--db <file>] [--strict|--permissive] [--codec zstd|none|<name>] [--assets|--no-assets] [--asset-types <mime,...>] [--with-enricher <name>] [--with-embedder <name>] [--dry-run] [--json]
weave rebuild <path>|--workspace <dir> [--db <file>] [--strict|--permissive] [--codec zstd|none|<name>] [--assets|--no-assets] [--asset-types <mime,...>] [--json]
weave sync <path>|--workspace <dir> [--db <file>] [--strict|--permissive] [--codec zstd|none|<name>] [--watch [--events]] [--json]
weave embeddings list|rebuild|drop <path> [--model <model>] [--dim <n>] [--keep-source] [--json]
weave codecs list [<path>] [--json]
weave export <path> --out <dir> --format raw|encrypted [--key-id <id>] [--yes] [--force] [--json]
weave workspace init|show|path [--workspace <dir>] [--json]
weave source add|remove|list|show [--workspace <dir>] [--prune] [--json]
weave extensions list [<path>] [--json]
weave extensions data list|get|gc <path> [--extension <name>] [--doc <id>] [--out <file>] [--force] [--dry-run] [--json]
weave config show|get|paths|path|init [--json]
weave completion bash|zsh|fish
weave mcp --bundle <path>|--workspace <dir> [--source <alias=path>] [--db <file>] [--stdio | --listen <addr>] [--token <token>] [--top-k-default <n>] [--allow-sensitive]
weave version [--json]
weave --version | --help
```

[`ROADMAP.md` §4](../../ROADMAP.md) owns the canonical CLI surface; keep this list and the roadmap
in sync when a command is added or removed.

## Machine Mode

`--json` emits exactly one `weave.cli/v1` envelope:

```json
{
  "contract": "weave.contract/v1",
  "cli": "weave.cli/v1",
  "ok": true,
  "result": {}
}
```

Rules:

- stdout contains only the envelope.
- stderr contains diagnostics and warnings.
- Failure envelopes are valid JSON and use the same contract.
- Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Runtime error, no matches, unknown concept, no route |
| 2 | Usage error, invalid root, invalid search parameters, confirmation required |
| 3 | Permission, privacy key or decryption failure |

- No network, daemon or interactive prompt.
- The parse cache is enabled by default; `--no-cache` disables it.

## Search Output

```sh
weave search <path> <query> --mode hybrid --top-k 10
```

- Mode defaults to `hybrid`; `--top-k` defaults to 10 and accepts 1..100.
- JSON responses always contain keyword, fuzzy and hybrid lists; `lexical` and `semantic` are
  additive and appear when those modes are selected.
- Human output:
  - hybrid: `<total_score> <title> [<path>]`
  - keyword: `<score> <title> [<matched keywords>]`
  - fuzzy: `<score> <title> [<matched fields>]`
- Empty selected list exits 1 with `weave: no matches` on stderr, but still emits a valid
  success envelope in JSON mode.
- Invalid mode/top-K exits 2 with `INVALID_REQUEST`.

## Version Discovery

`weave contract --json` returns versions, operations and error codes. Hosts call it once per
binary and fail fast on an unsupported contract major.

## Deferred Modes

`weave engine --stdio` and any legacy output format remain outside 0.7. They are not part of the
current contract.

## Testing

- Golden human and envelope output.
- Process tests for every command, including stdout/stderr and exit codes.
- Search mode/top-K boundary tests.
- Cache hit, invalidation and `--no-cache` parity.
- Determinism tests.
- Contract discovery test.

## Related Documents

- [Operations layer](operations.md)
- [Engine layer](engine-go.md)
- [Keyword + Fuzzy Search spec](../../specs/keyword-fuzzy-search.md)
- [Integration contracts](../integration/contracts.md)
- [Integration testing](../integration/testing.md)
