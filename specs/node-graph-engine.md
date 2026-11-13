---
type: specification
title: "Node Graph Engine Specification"
description: "Contract for building a bidirectional node graph from an OKF bundle, powering backlinks, pathfinding and CLI navigation."
tags:
  - "graph"
  - "engine"
  - "traversal"
  - "go"
  - "specification"
generated:
  by: opencode/deepseek-v4.1-flash
  at: "2026-10-26T00:00:00Z"
status: stable
---

# Specification: Node Graph Engine

## 1. Overview

Pure, offline Go package that turns a validated `contractv1.Bundle` into a bidirectional graph.
Each concept becomes a node with keywords; edges come from resolved bundle-relative Markdown links,
the frontmatter `related` array and validated extension-provided relations. The graph feeds
backlinks, pathfinding and CLI navigation.

There is no UI or graph serialization for a lens.

## 2. Package Structure

```text
engine/graph/
├── build.go       # Build, node/edge assembly, dangling links, sorting
└── traverse.go    # FindPath, Neighbors, OrphanNodes, counts
```

## 3. Contracts

### 3.1 GraphNode

`contractv1.GraphNode`:

- `id`: concept id
- `path`: bundle-relative path
- `type`
- `title`
- `keywords` (required)
- `status?`, `tags?`
- `in_degree`, `out_degree`

### 3.2 GraphEdge

`contractv1.GraphEdge`:

- `from`, `to`
- `source`: one of the relation kinds below
- `raw?`: original Markdown link text for `link` edges

Relation kinds:

- `link` — a Markdown link whose target resolves to an in-bundle concept
  (`resolves_in_bundle: true`).
- `related` — an entry in the concept's frontmatter `related` array. Bundle-relative paths, ids
  and optional `.md`/leading `/` are accepted.
- `contains` — structural containment from a repository or project to its files or projects. It is
  additive to the existing graph vocabulary and available to source providers.
- `imports` — a source file imports another file or external dependency.
- `declares` — a source file declares a symbol document.
- `references` — a document or symbol references another symbol.
- `calls` — a symbol calls another symbol.
- `inherits` — a type inherits another type.
- `implements` — a type implements an interface or trait.

Extension relations are defined by [Weave Code Extension](weave-code.md) and
[Weave Git Source Extension](weave-git.md) under
[ADR 0010](../architecture/adr/0010-extension-provided-graph-relations-and-project-analysis.md) and
[ADR 0011](../architecture/adr/0011-git-repositories-as-source-providers.md). Broken Markdown and
unresolved `related` targets are **not** edges; they are stored in `dangling` per source concept.
Unresolved extension targets become metadata only, or an external document when the same dependency
is referenced more than once.

### 3.3 Graph

The in-memory graph:

```go
type Graph struct {
    Nodes    map[string]contractv1.GraphNode
    Outgoing map[string][]contractv1.GraphEdge
    Incoming map[string][]contractv1.GraphEdge
    Dangling map[string][]contractv1.OkfLink
}
```

### 3.4 Build API

```go
func Build(bundle *contractv1.Bundle) *Graph
func SortedNodes(graph *Graph) []contractv1.GraphNode
func SortedEdges(graph *Graph) []contractv1.GraphEdge
```

### 3.5 Traversal API

```go
type TraversalOptions struct {
    Relations []string // empty means the default relation set
}

func FindPath(graph *Graph, from, to string, options TraversalOptions) []string
func Neighbors(graph *Graph, id string, options TraversalOptions) []string
func OrphanNodes(graph *Graph) []string
func NodeCount(graph *Graph) int
func EdgeCount(graph *Graph) int
```

Default relation set: `link`, `related`, `imports`, `declares`, `inherits`, `implements`, `contains`.
The `calls` and `references` kinds are excluded unless named explicitly. `OrphanNodes` and degree
counts consider every stored edge, independent of traversal filtering.

### 3.6 CLI Filtering

`weave path`, `weave relate` and `weave graph` accept `--relation <kind,...>`. The flag replaces the
default set and is validated against the complete relation list. An unknown kind is `INVALID_REQUEST`
with exit `2`. `weave graph` filters its edge list; `weave path` and `weave relate` restrict
traversal. Node counts, degree counts and orphan detection always use the full graph.

## 4. Data Flow

- Input: `contractv1.Bundle` from `engine/okf`.
- Create one node per concept.
- For each concept link with `resolves_in_bundle` and an existing target, add a `link` edge.
- For each `related` entry, resolve to a concept id and add a `related` edge.
- Append non-resolving/external links and unresolved `related` entries to `dangling`.
- Add validated extension relations after synthetic documents materialize; drop targets with fewer
  than two external references.
- Deduplicate edges by `(from, to, source)`.
- Build `incoming` by inverting `outgoing`.
- Compute in/out degrees.
- Feed the graph to list/show/backlinks/path and to search filtering/calibration if needed.

## 5. Edge Cases

- Empty bundle: empty graph, no error.
- Broken/external links: never crash; surfaced via `dangling`.
- Orphans: every concept is a node, even with zero edges.
- Duplicate edges: deduplicated per `(from, to, source)`.
- Self-links and cycles: allowed; traversal guards with a visited set.
- Missing/invalid concepts: parser excludes or marks them; the graph includes parsed concepts.
- Unresolved `related`: dangling, never an edge.
- Extension target with one reference: metadata only, no dangling edge.
- Extension target with two or more references: external document and edge.
- Mixed relation sets: path and relate filter by `TraversalOptions`; degrees and orphans do not.
- Determinism: nodes and serialized views sort by id; edges by `from`, `to`, `source`.

## 6. Performance

Graph build is O(V + E) with small constant overhead. The 10k-file budget remains under the overall
engine target.

## 7. Testing

- Golden conformance in `engine/conformance_test.go`.
- Unit tests for edges, degrees, dangling, BFS and cycles.
- Extension relation kinds, filtering, deduplication and the external reference threshold.
- Race suite.

## Related Concepts

- Depends on [OKF Bundle Parser](okf-bundle-parser.md)
- Depends on [OKF Bundle](../knowledge/concepts/okf-bundle.md)
- Feeds [Keyword + Fuzzy Search](keyword-fuzzy-search.md)
- Consumed by the Go CLI navigation operations
- Implements [Node Graph Engine](../knowledge/concepts/node-graph-engine.md)
