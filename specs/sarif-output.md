---
type: specification
title: "SARIF Audit Output Specification"
description: "Writes weave audit findings as a SARIF 2.1.0 log so code-scanning systems can display documentation gate failures."
tags:
  - "specification"
  - "audit"
  - "ci"
status: stable
---

# Specification: SARIF Audit Output

## 1. Overview

`weave audit` reports conformance and graph findings with stable codes. CI systems that display
code-scanning results read SARIF 2.1.0. This specification adds a SARIF output mode to `weave audit`, so
documentation gate failures can appear next to other findings. The audit findings, codes and gate
behavior do not change.

Non-goals:

- Changing finding codes, severities or `--fail-on` semantics.
- Source locations below the document level. Audit findings have no line numbers in the current contract.
- Uploading results anywhere. Weave writes the log to stdout or a file only.

## 2. Contract

### 2.1 Syntax

```sh
weave audit <path> --format sarif [--out <file>] [--fail-on error|warning|none]
```

- SARIF output is its own format. It is not wrapped in a `weave.cli/v1` envelope.
- `--format sarif` and `--json` are mutually exclusive: `INVALID_REQUEST`, exit `2`.
- Without `--out`, the log goes to stdout. With `--out`, the file is written only after the log is complete.

### 2.2 Mapping

| Weave | SARIF |
| --- | --- |
| Finding code | `rules[].id` and `results[].ruleId` |
| Severity `error` | `level` `error` |
| Severity `warning` | `level` `warning` |
| Severity `info` | `level` `note` |
| Finding message | `results[].message.text` |
| Document path, bundle-relative POSIX | `locations[].physicalLocation.artifactLocation.uri` |

- `tool.driver.name` is `weave`. `tool.driver.version` is the running binary version.
- The log uses SARIF version `2.1.0` and its published schema URI.
- Results are sorted by URI, then rule identifier, then message, so output is deterministic.

### 2.3 Gate and exit status

`--fail-on` decides the exit status exactly as it does for the human and JSON outputs. The SARIF log is
written before the exit status is set, so a failing gate still produces a complete log.

## 3. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| `--format` with `--json` | `INVALID_REQUEST` | `2` |
| Unknown format | `INVALID_REQUEST` | `2` |

## 4. Testing

- Golden SARIF log for the audit fixture bundles, with severity mapping for each level.
- Results ordering is stable across runs.
- Exit status matches `--fail-on` for each gate value.
- The log validates against the SARIF 2.1.0 schema.

## 5. Acceptance Criteria

1. A failing audit produces a SARIF log that a code-scanning import accepts.
2. Exit status is unchanged from the non-SARIF output for the same bundle.

## Related Documents

- [Weave Audit](weave-audit.md)
- [Machine output](https://github.com/prulloac/weave-docs/blob/main/architecture/adr/0002-config-paths-and-db-location.md)
