---
type: specification
title: "Search Field Filters Specification"
description: "Repeatable --where filters on weave search that narrow results by document type, status, tag and keyword without changing ranking."
tags:
  - "specification"
  - "search"
  - "filters"
status: draft
---

# Specification: Search Field Filters

## 1. Overview

`weave search` returns ranked hits for a query. Users often need only documents of one type or with one
status. This specification adds repeatable `--where field:value` filters that remove non-matching hits.
Filters narrow the result set; they never change scores or order.

Non-goals:

- Changing ranking, scoring weights or calibration baselines.
- Free-text filters, ranges, negation or boolean expressions.
- MCP tool arguments; the MCP surface follows in a separate change.
- Filters on `weave explain`.

## 2. Contract

### 2.1 Syntax

```sh
weave search <path> <query> [--where <field>:<value> ...] [--mode ...] [--top-k <n>] --json
```

- `--where` repeats. Each occurrence adds one filter.
- Filters combine with AND. Two filters on the same field both must match.
- The value is matched exactly after trimming surrounding whitespace.

### 2.2 Fields

| Field | Matches | Case |
| --- | --- | --- |
| `type` | the document `type` | case-sensitive |
| `status` | the document `status` | case-sensitive |
| `tag` | a value in the document `tags` list | case-sensitive |
| `keyword` | a value in the document `keywords` list | case-insensitive |

Unknown fields and empty values fail with `INVALID_REQUEST`, exit `2`, before any search runs.

### 2.3 Semantics

- Filters apply to every hit list the requested mode produces (keyword, fuzzy, BM25, hybrid and
  semantic).
- Filtering happens before the top-K cut, so up to K matching hits are returned when they exist.
- Relative order of remaining hits is unchanged.
- Documents that are invalid for keyword search (missing `keywords`) can still match `type`, `status` and
  `tag` filters, because those filters do not use keywords.
- Filters work with persistent and `--no-db` searches.

### 2.4 Output

The search result gains one additive field, `filters`, listing the applied filters in the order given.
Without `--where`, the field is omitted and output is unchanged.

## 3. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| Filter without `:` or with an unknown field | `INVALID_REQUEST` | `2` |
| Empty value | `INVALID_REQUEST` | `2` |

## 4. Testing

- Each field matches and does not match.
- Two filters on one field both apply.
- Top-K returns K matches after filtering when available.
- Scores and order of unfiltered results are unchanged for the same query.
- Calibration corpus runs unchanged.

## 5. Acceptance Criteria

1. A reader can narrow a search to one document type with a single flag.
2. Filtering never changes a score or the relative order of the hits it keeps.
3. Invalid filters fail before any database or extension work.

## Related Documents

- [Keyword + Fuzzy Search](keyword-fuzzy-search.md)
- [BM25 Ranking](bm25-ranking.md)
- [Weave Explain](weave-explain.md)
