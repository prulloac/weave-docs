---
type: specification
title: "Graph Export Formats Specification"
description: "Renders the document graph as Graphviz DOT, Mermaid or GraphML for visualization outside Weave, with deterministic output."
tags:
  - "specification"
  - "graph"
  - "export"
status: draft
---

# Specification: Graph Export Formats

## 1. Overview

`weave graph` returns the document graph as JSON. Some users want to draw it in existing tools. This
specification adds a text format option that renders the same graph as Graphviz DOT, Mermaid or
GraphML. Rendering is a view of the graph; it never changes what is stored.

Non-goals:

- Rendering images, HTML or an interactive viewer. Weave has no UI.
- Exporting bundle content or document bodies. Only node identifiers, titles and edge kinds are written.
- Changing the JSON graph contract.

## 2. Contract

### 2.1 Syntax

```sh
weave graph <path> --format dot|mermaid|graphml [--relation <kind,...>] [--out <file>]
```

- Without `--out`, output goes to stdout.
- With `--out`, the file is written only after rendering succeeds. A failure leaves no partial file.
- `--format` and `--json` are mutually exclusive: `INVALID_REQUEST`, exit `2`.
- `--relation` uses the same filter and default relation policy as the JSON graph.

### 2.2 Content

- Nodes: every concept, plus extension-synthetic documents that the graph contains. Label is the title
  when present, otherwise the identifier.
- Edges: one per graph edge, labelled with its relation kind.
- Dangling targets (edges to documents that are not present) are omitted and counted in one stderr
  warning.

### 2.3 Determinism

- Nodes are sorted by identifier.
- Edges are sorted by source, target and kind.
- The same bundle and options always produce byte-identical output.

### 2.4 Format rules

- DOT: node identifiers and labels are quoted, and `"` and `\` are escaped.
- Mermaid: node identifiers are rewritten to `[A-Za-z0-9_]` and the original identifier is kept as the
  label. Labels escape Mermaid-reserved characters.
- GraphML: well-formed XML, one `key` for the label and one for the relation kind, with all text escaped.

## 3. Errors

| Condition | Code | Exit |
| --- | --- | --- |
| Unknown format | `INVALID_REQUEST` | `2` |
| `--format` with `--json` | `INVALID_REQUEST` | `2` |
| Cannot write `--out` | `PERMISSION_DENIED` or `INVALID_REQUEST` | `2` or `1` |

## 4. Testing

- Golden files for each format from a fixed bundle.
- Escaping of quotes, backslashes and XML characters in titles.
- Determinism across repeated runs.
- Dangling targets are omitted with one warning.
- `--out` leaves no file when rendering fails.

## 5. Acceptance Criteria

1. `weave graph --format dot` output renders in Graphviz without edits.
2. Two runs over the same bundle produce identical bytes.
3. No document body appears in any format.

## Related Documents

- [Node Graph Engine](node-graph-engine.md)
- [Weave Relate](weave-relate.md)
- [Bundle Export](bundle-export.md)
