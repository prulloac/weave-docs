---
type: specification
title: "Per-Type Frontmatter Schemas"
description: "Opt-in JSON Schema files under .weave/types that refine the frontmatter contract for one document type, validated by ingest, sync, rebuild and audit."
tags:
  - "bundle"
  - "schema"
  - "ingest"
  - "audit"
status: draft
---

# Per-Type Frontmatter Schemas

## 1. Overview

A bundle can refine the frontmatter contract per document type by adding
`.weave/types/<type>.schema.json`. The base Weave profile still applies; the schema adds required
fields, types and constraints. Validation runs wherever documents enter the index and in `audit`, so
both surfaces agree. The decision is
[ADR 0020](../architecture/adr/0020-per-type-frontmatter-schemas.md).

## 2. Contract

### 2.1 Layout

```text
<path>/.weave/types/
  adr.schema.json
  runbook.schema.json
```

- A document whose `type` is `adr` is validated by `adr.schema.json` when the file exists.
- Type names are `[a-z0-9][a-z0-9._-]*`. A type that does not map to a file is not an error; it uses
  the base profile only.
- The directory is optional. Without it, behavior and output are unchanged.

### 2.2 Schema rules

- Files use JSON Schema 2020-12 as implemented by `jsonschema/v6`.
- `$ref` may point inside the same file or another file under `.weave/types`. Remote `$ref`, `http(s)`
  URIs and network access are `TYPE_SCHEMA_UNSUPPORTED`.
- The schema validates frontmatter only. `type` and `keywords` remain required by the base profile and
  cannot be relaxed.
- Unknown frontmatter properties are allowed unless the schema sets `additionalProperties: false`.
- Schema files are never generated, downloaded or edited by Weave.

### 2.3 Validation points

| Command | Behavior |
| --- | --- |
| `ingest`, `sync`, `rebuild` | Validate each document before it enters the index |
| `audit` | Report one finding per violation, severity `error` |
| `--permissive` ingest | Downgrade violations to warnings and index the document |
| `--no-db` read commands | Do not validate; they do not write |

- A schema load failure (invalid JSON, unsupported ref, invalid type file name) fails the command
  before any document is processed, even with `--permissive`.
- Validation is deterministic and has no network or extension calls.

### 2.4 Output

- Strict ingest failure is `TYPE_SCHEMA_INVALID`, exit `1`, with the document path and each violation
  (`instancePath`, message).
- Permissive ingest exits `0` and adds one warning per document that lists its violations.
- `audit` results keep their existing shape; the finding code is `TYPE_SCHEMA_INVALID` and its message
  names the document and the first violation. `--fail-on` and exit codes are unchanged.

## 3. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| Document violates its type schema (strict ingest) | `TYPE_SCHEMA_INVALID` | `1` |
| Schema file invalid or type file name invalid | `TYPE_SCHEMA_INVALID` | `1` |
| Remote or unsupported `$ref` | `TYPE_SCHEMA_UNSUPPORTED` | `1` |
| Missing `type` or `keywords` | existing base-profile code | unchanged |

## 4. Testing

- A valid document passes with and without a schema.
- A missing required field fails strict ingest and warns under `--permissive`.
- `additionalProperties: false` rejects an extra field only when declared.
- A schema for one type does not affect another type.
- A local `$ref` across two files works; a remote `$ref` is `TYPE_SCHEMA_UNSUPPORTED`.
- An invalid schema fails before any document is indexed.
- `audit` and ingest report the same violation for the same document.
- Bundles without `.weave/types` produce byte-identical output to today.

## 5. Acceptance Criteria

1. A bundle can require extra frontmatter fields for one type without changing any other type.
2. Ingest and audit agree on every violation.
3. Invalid schemas fail clearly and never partially index a bundle.
4. No network access and no change to bundles that do not opt in.

## Related Documents

- [ADR 0020](../architecture/adr/0020-per-type-frontmatter-schemas.md)
- [OKF Bundle Parser](okf-bundle-parser.md)
- [Weave Audit](weave-audit.md)
