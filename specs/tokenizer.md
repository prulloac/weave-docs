---
type: specification
title: "Pluggable Tokenizer Role"
description: "Opt-in tokenizer extensions that supply index terms and query expansions for keyword and BM25 search, with the tokenizer identity recorded in the index."
tags:
  - "search"
  - "extensions"
  - "tokenization"
  - "ranking"
status: draft
---

# Pluggable Tokenizer Role

## 1. Overview

Keyword and BM25 search tokenize text with the built-in tokenizer. This specification adds an opt-in
`tokenizer` extension role that returns the term stream for indexing and, at query time, additional
terms for synonym expansion. Stemming is expressed by returning stems; synonyms are query-only.

The default path does not change. A tokenizer is selected explicitly, its identity is recorded in the
index, and changing it requires a rebuild. The decision and its rationale are in
[ADR 0018](../architecture/adr/0018-pluggable-tokenizer-role.md).

## 2. Contract

### 2.1 Selection

```sh
weave ingest  <path> --db <db> --tokenizer <name> --json
weave rebuild <path> --db <db> --tokenizer <name> --json
weave sync    <path> --db <db> --tokenizer <name> --json
weave search  <path> "<query>" --tokenizer <name> --json
```

- `--tokenizer` names one `weave-<name>` extension whose manifest declares the `tokenizer` role.
- Without `--tokenizer`, the built-in tokenizer runs and output is byte-identical to today.
- A tokenizer is never selected implicitly from a bundle or manifest.
- `search --no-db` may select any tokenizer; a persistent search must use the tokenizer recorded in
  the index.

### 2.2 Request

```json
{
  "v": "weave.cli/v1",
  "type": "tokenizer_request",
  "text": "Tokenization normalizes text",
  "language": "en",
  "mode": "index",
  "options": {}
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `text` | yes | The text to tokenize, after privacy handling |
| `language` | no | BCP 47 hint; core sends the document language when known |
| `mode` | yes | `index` or `query` |
| `options` | no | Opaque, extension-defined |

### 2.3 Response

```json
{
  "v": "weave.cli/v1",
  "type": "tokenizer_response",
  "terms": ["token", "normal", "text"],
  "expansions": {"token": ["tokenize", "tokenization"]}
}
```

- `terms` is the ordered term stream written to the index, or used to build the query.
- `expansions` is valid only in `query` mode. It maps a term in `terms` to additional query terms.
- The same `text`, `language`, `mode` and tokenizer identity must produce the same `terms`.
- Terms are lower-cased by the extension if it wants case folding; core does not re-case them.

### 2.4 Index identity

The index metadata records `tokenizer_name`, `tokenizer_version` and, when the manifest supplies it,
`tokenizer_cache_key`. Opening an index with a different identity is `TOKENIZER_CHANGED`, exit `1`,
with a hint naming `weave rebuild <path> --tokenizer <name>`.

- A persistent search uses the recorded tokenizer regardless of the flag.
- Passing `--tokenizer` with a different name is `TOKENIZER_CHANGED`.
- `--no-db` has no stored identity and performs no comparison.
- The built-in tokenizer records `builtin` as its name and the core contract version as its version.

### 2.5 Bounds

| Limit | Value |
| --- | --- |
| Input text per request | 1 MiB |
| Terms per response | 4096 |
| Term length | 128 bytes |
| Expansions per term | 32 |
| Expansions total | 4096 |
| Default timeout | 5 s, `--timeout` overrides |

## 3. Behavior

- Keyword and BM25 index and query paths use the tokenizer terms in place of the built-in terms.
- Query expansions add terms to the same field with the same operator; they never change scores of
  documents that already matched.
- Fuzzy and semantic search are unchanged.
- A tokenizer failure during a write fails that write with `TOKENIZER_PROTOCOL` or
  `TOKENIZER_TIMEOUT`; no partial index is committed.
- A tokenizer failure during `--no-db` search falls back to the built-in tokenizer and adds one
  warning; a persistent search cannot fall back because its index already uses the stored terms.

## 4. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| No tokenizer with that name | `TOKENIZER_NOT_FOUND` | `2` |
| Manifest requirement unmet | `EXTENSION_REQUIREMENT_UNMET` | `1` |
| Index and request tokenizer differ | `TOKENIZER_CHANGED` | `1` |
| Invalid response or bound violation | `TOKENIZER_PROTOCOL` | `1` |
| Timeout | `TOKENIZER_TIMEOUT` | `1` |

## 5. Testing

- Default output and calibration are unchanged without `--tokenizer`.
- A stemming fixture makes `running` match `run`; the same query without the tokenizer does not.
- A query-expansion fixture makes `db` match `database` only when the tokenizer is active.
- Swapping tokenizers on an existing index fails with `TOKENIZER_CHANGED`; `rebuild` succeeds.
- A malformed response, an oversized term list and a timeout each fail the write with the right code.
- A `--no-db` search falls back with one warning.
- Encrypted or redacted text is absent from the request.

## 6. Acceptance Criteria

1. A tokenizer can be selected for ingest, rebuild, sync and search, and the index records it.
2. Without a tokenizer, behavior, output and calibration are unchanged.
3. A tokenizer change on an existing index is refused, not silently applied.
4. Stemming and query expansions work without changing the score of an existing match.

## Related Documents

- [ADR 0018](../architecture/adr/0018-pluggable-tokenizer-role.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [BM25 Ranking](bm25-ranking.md)
- [Keyword and Fuzzy Search](keyword-fuzzy-search.md)
