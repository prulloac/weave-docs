---
type: Architecture Decision Record
title: "ADR 0018: Pluggable Tokenizer Role"
description: "Reverses the no-stemming and no-synonyms non-goal through an opt-in tokenizer extension role, with the tokenizer identity recorded in the index and a rebuild required when it changes."
tags:
  - "architecture"
  - "extensions"
  - "search"
  - "ranking"
status: accepted
---

# ADR 0018: Pluggable Tokenizer Role

## Context

Keyword and BM25 search use the tokenizer built into the SQLite index. The roadmap records "no
synonyms or stemming yet" as a non-goal, so writers of non-English content, and readers who search
for a different inflection than the author used, get weaker results than the ranking model allows.
Embeddings cover some of that gap, but they are a separate semantic path and do not help exact or
prefix keyword search.

The owner approved a tokenizer role as an opt-in extension. It must not change the default index or
the calibration baseline, and it must not pretend that swapping tokenizers on an existing index is
safe: term sets are part of the index, so a change invalidates it.

## Decision

1. **One `tokenizer` role over `weave.cli/v1`.** A tokenizer is a `weave-<name>` executable selected
   with `--tokenizer <name>` on `ingest`, `rebuild`, `sync` and `search`. The role is declared in the
   manifest `roles` list and implemented through the role descriptor registry (ADR 0013).
2. **Two operations, one stream.** `tokenizer_request` carries `text`, an optional `language` hint,
   `mode` (`index` or `query`) and opaque `options`; `tokenizer_response` carries an ordered `terms`
   list. In `query` mode the response may also carry `expansions`, mapping a term to additional query
   terms. Stemming is expressed by returning stems as `terms`; synonyms are expressed only as query
   expansions so the index does not grow with every synonym.
3. **The index records its tokenizer.** The index metadata stores the tokenizer name, its manifest
   `version`, and an opaque `cache_key` when the manifest provides one (see enrichment caching).
   Opening an index with a different identity fails with `TOKENIZER_CHANGED`, exit `1`, and a hint to
   run `weave rebuild <path> --tokenizer <name>`.
4. **Search must match the index.** A search uses the tokenizer recorded in the index; passing a
   different `--tokenizer`, or none when the index has one, is `TOKENIZER_CHANGED`. `--no-db` searches
   may use `--tokenizer` with no identity check because they build a transient index.
5. **The default is unchanged.** Without `--tokenizer`, the built-in tokenizer runs and the existing
   calibration baseline, index shape and output bytes do not change. A tokenizer is never selected
   implicitly from a bundle or manifest.
6. **Privacy applies before tokenization.** The tokenizer receives the searchable text after privacy
   handling, never ciphertext or protected spans. It must not read the index, the bundle or the
   database, and core does not send it document ids it does not need.
7. **Determinism and bounds.** The same text, mode, language and tokenizer identity must produce the
   same terms. Core bounds input size, term count, term length and expansion count; a violation is
   `TOKENIZER_PROTOCOL` and falls back to the built-in tokenizer for `--no-db` queries, or fails the
   write when an index would otherwise be built with an unusable tokenizer.
8. **Calibration.** A tokenizer is opt-in, so the committed baseline is unaffected. Any change to the
   built-in tokenizer, or a future default, needs a calibration review like any ranking change.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Stemming in core | Rejected: it hardcodes languages and reverses the extension boundary |
| Tokenizer chosen per document | Rejected: one index has one term space |
| Synonyms stored at index time | Rejected: it multiplies the index for a query-time feature |
| Reuse the enricher role | Rejected: enrichment is per document and returns metadata, not the index token stream |
| Embeddings instead | Rejected: semantic search does not replace exact and prefix keyword behavior |

## Consequences

- New spec work: `weave-docs/specs/tokenizer.md` with request/response, errors and BDD scenarios.
- Index schema gains tokenizer metadata; a rebuild path is required before release.
- Search error handling gains `TOKENIZER_CHANGED` and `TOKENIZER_PROTOCOL`.
- The authoring guide gains a tokenizer section; the non-goal in the roadmap is marked reversed.
- The first release supports stemming and query expansions only; language detection and
  multi-tokenizer indexes stay out of scope.
