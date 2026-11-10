---
type: specification
title: "Weave Code Extension Specification"
description: "First-party code knowledge extension: static parsing, project-wide symbols and relationships, optional symbol documents, and extension-provided graph edges."
tags:
  - "specification"
  - "code"
  - "extensions"
  - "graph"
  - "0.8"
status: stable
generated:
  by: opencode/deepseek-v4.1-flash
---

# Specification: Weave Code Extension

## 1. Overview

`weave-code` turns source files into Weave documents. It is a standalone `weave-<name>` extension,
like `weave-image`, and speaks `weave.cli/v1`. It never imports the Weave engine and never executes
the code it reads.

The extension is both an **enricher** and a **project analyzer**. Weave invokes it once per project
write, passes the bundle root and the list of source files, and receives:

- one enriched document per source file;
- optional symbol documents;
- optional external dependency documents;
- graph relations between files and symbols.

## 2. Decisions

These decisions are fixed for the first version:

| Area | Decision |
| --- | --- |
| Languages | Go, Python, JavaScript, TypeScript, Rust, C, C++, Java, Scala, Dart, Zig |
| Parser strategy | Static binaries with no C libraries; pure-Go tree-sitter runtime or WebAssembly grammars; lexical fallback |
| Relationships | Core extension-provided graph edges, not extension data only |
| Relationship depth | Imports, references, calls, inheritance and implementation |
| Document granularity | One document per source file by default; symbol documents opt-in |
| Ingestion trigger | Only when `--with-enricher code` is present |
| Code detection | Known source extensions only |
| Cross-file resolution | One project-wide analysis pass per write |
| Default traversal | Imports, inheritance and implementation; calls and references opt-in |
| Symbol identity | `<file>#<symbol>` |
| Unresolved targets | Metadata only, unless an external dependency is referenced more than once |
| File-to-symbol traversal | `declares` traversed by default |
| Synthetic export | `_code/symbols.json` and `_code/relations.json`, plus warnings |
| Analysis cache | `WEAVE_CACHE_DIR`, never inside the bundle |
| Generated code | Skipped by default, opt-in through configuration |
| External identity | `_code/external/<language>/<qualified-name>` |

## 3. Non-Goals

- Executing, building, compiling, formatting or editing source code.
- Language servers, compilers, package managers or network resolution.
- Binary code artifacts such as `.class`, `.jar`, `.o`, `.so`, `.dll` or `.wasm`.
- Semantic code embeddings in the first version.
- Type checking or full name resolution across external dependencies.
- Writing into the source bundle.
- Supporting generated or minified files beyond best-effort parsing.

## 4. Languages and Detection

### 4.1 Source extensions

Only these extensions are scanned:

| Language | Extensions |
| --- | --- |
| Go | `.go` |
| Python | `.py` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Rust | `.rs` |
| C | `.c`, `.h` |
| C++ | `.cc`, `.cpp`, `.cxx`, `.hpp`, `.hh`, `.hxx` |
| Java | `.java` |
| Scala | `.scala`, `.sc` |
| Dart | `.dart` |
| Zig | `.zig` |

A file is included only when its content is valid UTF-8 without NUL bytes. Files larger than
**4 MiB** are skipped with a warning; the project limit is **512 MiB** and **10,000 files**.

### 4.2 Media types

Core currently sniffs text and records `text/plain`, discarding the extension type. This
specification requires:

- known source extensions keep their language media type (`text/x-go`, `text/x-python`,
  `text/x-rust`, `text/x-java`, and so on) when the bytes are valid UTF-8;
- the media mismatch warning is not emitted for a known text extension whose bytes match text;
- unknown text files remain `text/plain`;
- no language allowlist is needed for classification beyond the table above.

### 4.3 Ignored paths

Core asset discovery already ignores `.git`, `node_modules`, `.weave`, hidden directories and
temporary files. The project analyzer also ignores:

- `vendor`, `target`, `build`, `dist`, `out`, `coverage`;
- generated files matching `*.gen.*`, `*.generated.*`, `*.min.js`, `*.min.css`;
- configured ignore patterns in `.weave/code.yaml`.

Generated files are skipped by default. Setting `parse_generated: true` in `.weave/code.yaml`
opts them back in.

## 5. Document Model

### 5.1 Source file document

| Field | Value |
| --- | --- |
| `id` and `path` | bundle-relative source path |
| `content_kind` | `blob` (text-readable blob) |
| `doc_type` | `Code` |
| `media_type` | language media type |
| `title` | package or module name plus file name |
| `description` | leading package, module or file documentation |
| `keywords` | language, package, module, exported symbols, imports |
| `body` | original source text, stored raw and indexed directly |
| `content_metadata` | language, package, module, parser, export count, line count, parse status |

Source files remain retrievable with `weave show --out`, exportable, and searchable by body text.

### 5.2 Symbol document

Symbol documents are disabled by default. Enable them with either:

```sh
WEAVE_CODE_SYMBOL_DOCUMENTS=1 weave ingest ~/repo --with-enricher code
```

or `.weave/code.yaml`:

```yaml
symbol_documents: true
```

Identity is `<file>#<symbol>`, for example `src/main.go#main` or
`src/server.go#Server.Start`. Nested symbols use dot-separated names.

| Field | Value |
| --- | --- |
| `id`, `path` | `<file>#<symbol>` |
| `content_kind` | `symbol` |
| `doc_type` | `CodeSymbol` |
| `title` | qualified symbol name |
| `description` | doc comment or leading comment |
| `keywords` | symbol name, package, receiver, referenced symbols |
| `body` | signature plus doc comment, never the whole file |
| `content_metadata` | kind, signature, visibility, parent symbol, line range |

Symbol documents are synthetic: raw export does not write a file at `path#symbol`. Export writes
`_code/symbols.json` and `_code/relations.json`, then emits one warning per synthetic document
excluded from the file tree.

### 5.3 External dependency document

An external target is a dependency, symbol, call target or base type that is not a document in the
bundle. It becomes a standalone document only when it is referenced **more than once**.

Identity:

```text
_code/external/<language>/<qualified-name>
```

Examples: `_code/external/go/fmt.Println`, `_code/external/java/java.util.List`. On collision, append
`~<first-eight-sha256>`.

| Field | Value |
| --- | --- |
| `content_kind` | `symbol` |
| `doc_type` | `CodeExternal` |
| `title` | qualified external name |
| `description` | module path or package |
| `keywords` | language, qualified name, importing files |
| `body` | qualified name and relationship summary |
| `content_metadata` | language, package, reference count, relationship kinds |

A single-reference external target stays in the referring document's metadata and extension data.
It does not become a document and does not create a graph edge.

## 6. Project Analysis Protocol

Per-file enrichment cannot resolve cross-file calls, references or inheritance. The extension adds a
new `weave.cli/v1` message pair.

### 6.1 Request

```json
{
  "v": "weave.cli/v1",
  "type": "project_analysis_request",
  "bundle_root": "/home/user/repo",
  "files": [
    {
      "id": "src/main.go",
      "path": "src/main.go",
      "media_type": "text/x-go",
      "content_hash": "sha256:..."
    }
  ],
  "options": {
    "symbol_documents": true,
    "relations": ["imports", "references", "calls", "inherits", "implements"]
  }
}
```

Rules:

- One request per ingest, rebuild or sync when `--with-enricher code` is present.
- `files` contains every discovered source file, ordered by ID.
- Core does not send file bytes; the extension reads `bundle_root`/`path`.
- `content_hash` lets the extension reuse its own cache.
- Default timeout is **120 seconds**; `--timeout` overrides it.
- Request limit is **64 MiB**.

### 6.2 Response

```json
{
  "v": "weave.cli/v1",
  "documents": [
    {
      "id": "src/main.go",
      "title": "main package",
      "description": "Command entrypoint.",
      "keywords": ["go", "main", "run"],
      "content_metadata": {"v": 1, "language": "go", "package": "main"},
      "symbol_documents": [
        {
          "id": "src/main.go#main",
          "title": "main",
          "body": "func main()",
          "content_metadata": {"v": 1, "kind": "function"}
        }
      ]
    }
  ],
  "external_documents": [],
  "relations": [
    {"from": "src/main.go", "to": "src/server.go", "kind": "imports"},
    {"from": "src/main.go#main", "to": "src/server.go#Run", "kind": "calls"}
  ],
  "warnings": []
}
```

Rules:

- Every request file appears exactly once in `documents` unless it failed to parse; failed files
  return a warning and keep the file document with lexical metadata.
- Unknown response fields are ignored.
- `v` must be `weave.cli/v1`.
- Response limit is **64 MiB**. Oversized responses are `EXTENSION_PROTOCOL`; ingestion fails in
  strict mode and warns in permissive mode.

### 6.3 Synchronization

- `ingest` and `rebuild` run a full project analysis.
- `sync` with a project analyzer is deferred in the first delivery slice: it returns
  `INVALID_REQUEST` and instructs the operator to run `weave rebuild`. Incremental project analysis
  needs the extension cache and a dedicated apply path.
- When incremental analysis lands, `sync` runs project analysis over the current file list. The
  extension may use `content_hash` and its own cache under `WEAVE_CACHE_DIR` to avoid reparsing
  unchanged files.
- A future incremental response must still contain the full relation set; cached analysis is allowed.
- If the cache is missing or invalid, the extension performs a full parse.

## 7. Relationships

### 7.1 Kinds

| Kind | From | To | Meaning |
| --- | --- | --- | --- |
| `imports` | file | file or external module | Source file imports another file or package |
| `declares` | file | symbol | Source file declares a symbol |
| `references` | file or symbol | symbol or external symbol | Symbol reference |
| `calls` | symbol | symbol or external symbol | Call expression |
| `inherits` | symbol | symbol or external symbol | Class or type inheritance |
| `implements` | symbol | symbol or external symbol | Interface or trait implementation |

`inherits` and `implements` are both inheritance relations. `declares` links a file to its symbols.

### 7.2 Core graph contract

Graph edges gain these values in the existing `source` field:

```text
link, related, imports, declares, references, calls, inherits, implements
```

- Extension relations are validated against existing document IDs after all documents are written.
- A relation to an external target creates an external document only when the target is referenced
  more than once.
- A single-reference external target is dropped from the graph and kept in metadata.
- Duplicate edges with the same `from`, `to` and kind collapse to one.
- Relation targets never create dangling Markdown-style links.

### 7.3 Traversal

`weave path` and `weave relate` gain:

```sh
--relation <kind,...>
```

- Default traversable kinds: `link`, `related`, `imports`, `declares`, `inherits`, `implements`.
- `references` and `calls` are excluded unless named in `--relation`.
- `--relation` replaces the default set; it accepts every kind above.
- Existing `--depth` limits apply.
- `weave graph` reports all edges with their kind and supports `--relation` filtering.

## 8. Metadata and Keywords

Per source file:

- language, package or module, imports, exported symbols, line count, parser name and parser version;
- parser status: `parsed`, `partial` or `fallback`;
- source hash and line ranges for symbols.

Per symbol:

- kind (function, method, type, class, interface, trait, enum, constant, variable, module);
- signature, visibility, parent symbol, receiver, line range, doc comment;
- called, referenced and inherited names.

Keywords are generated from the language, package, module, exported symbol names, imported module
names and a bounded doc-comment vocabulary. The extension bounds keywords to 64 per document and
never copies the full source into keywords.

## 9. CLI and Configuration

```sh
weave ingest ~/repo --with-enricher code --db ~/.weave/index.db --json
weave rebuild ~/repo --with-enricher code --db ~/.weave/index.db --json
weave sync ~/repo --with-enricher code --db ~/.weave/index.db --json
weave search ~/repo "parse request" --json
weave relate ~/repo src/main.go#main --depth 2 --relation imports,calls --json
weave path ~/repo src/main.go#main src/server.go#Run --relation imports,declares,calls --json
```

- `--with-enricher code` triggers source discovery without `--assets` or `--asset-types`.
- `--no-code` is not required because code scanning is never implicit.
- `weave list ~/repo --type Code`, `--type CodeSymbol` and `--type CodeExternal` filter the
  generated document types.
- Symbol documents are controlled only by `.weave/code.yaml` or `WEAVE_CODE_SYMBOL_DOCUMENTS`.
- Ignore patterns live in `.weave/code.yaml` under `ignore`.

Example configuration:

```yaml
symbol_documents: true
parse_generated: false
ignore:
  - "third_party/**"
  - "**/*_test.go"
```

## 10. Limits and Resource Use

| Limit | Value |
| --- | --- |
| Source files per project | 10,000 |
| Source bytes per project | 512 MiB |
| Source file size | 4 MiB |
| Project request | 64 MiB |
| Project response | 64 MiB |
| Project timeout | 120 seconds default |
| Symbol documents per file | 2,000 |
| Relations per project | 1,000,000 |
| Keywords per document | 64 |
| Doc comment text | 64 KiB per document |

Exceeding a limit produces a warning where recovery is possible and
`EXTENSION_PROTOCOL` where it is not.

## 11. Privacy and Security

- Source bytes are read by a trusted local extension; core never executes them.
- The extension must not invoke compilers, build tools, package managers, language servers or the
  network.
- Automatically ingested source may contain secrets. The operator opts in by naming the code
  enricher; Weave does not scan for secrets.
- Ignore rules must be applied before reading file bytes.
- Source bodies follow the existing blob privacy model; encrypted blob export remains deferred.
- Symbol and external documents contain signatures and documentation only, never full file bodies.
- Extension failures never corrupt the previous index; strict mode fails the write, permissive mode
  warns and keeps the file documents.

## 12. Failure Handling

| Condition | Behavior |
| --- | --- |
| Missing `weave-code` | Exit `2` with `EXTENSION_NOT_FOUND` |
| Parse failure for one file | Warning; lexical metadata; file document kept |
| Unknown language | File is skipped because only known extensions are scanned |
| Project timeout | Strict fails; permissive keeps previous code metadata |
| Malformed response or wrong version | `EXTENSION_PROTOCOL`; strict fails; permissive warns |
| Candidate target missing | Metadata only if single reference; external document if repeated |
| Duplicate relation | Deduplicated silently |
| Symbol document limit exceeded | Warning; remaining symbols stay as file metadata |

## 13. Testing

- Extension process tests with fixture repositories for all eleven languages.
- Parser fallback tests with malformed and partial files.
- Source extension detection and media type preservation.
- Project analysis request and response validation, ordering and limits.
- Cross-file imports, references, calls, inheritance and implementation.
- External target threshold: one reference versus two references.
- Symbol document identity and optional enablement.
- Raw export skipping synthetic documents and writing `_code/symbols.json` and
  `_code/relations.json`.
- Graph edge values, deduplication, `--relation` filtering and depth limits.
- `weave path` and `weave relate` across code and Markdown edges.
- Automatic scanning only with `--with-enricher code`.
- Ignore patterns, generated files and secret-free fixtures.
- Full gate, race suite and calibration unchanged without the code enricher.

## 14. Acceptance Criteria

1. Only `--with-enricher code` triggers source discovery.
2. All eleven languages parse with a static, C-free binary or fall back cleanly.
3. File documents are text blobs with language media types and searchable source bodies.
4. Symbol documents are optional, use `<file>#<symbol>`, and never export as source files.
5. Cross-file imports, references, calls, inheritance and implementation resolve in one project pass.
6. External targets become documents only after more than one reference.
7. Core graph carries the six code relation kinds and validates them against document IDs.
8. `weave path` and `weave relate` traverse imports, declares, inheritance and implementation by
   default; calls and references require `--relation`.
9. Existing Markdown-only behavior and all golden outputs are unchanged without the code enricher.
10. The 1.0 stability window is unaffected when the extension is not installed.

## 15. Delivery Slices

| Slice | Scope |
| --- | --- |
| C1 | Core media type preservation, project analysis protocol and graph relation contract |
| C2 | `weave-code` discovery, Go and Python parsers, file documents and metadata |
| C3 | Remaining languages and lexical fallback |
| C4 | Cross-file relations, external documents and optional symbol documents |
| C5 | `--relation` traversal, export behavior, tests and documentation |

Each slice is a separate stacked pull request. C1 must not change output without the code enricher.

## 16. Resolved Decisions

- `declares` is traversed by default so a source file can reach its symbols.
- Raw export writes `_code/symbols.json` and `_code/relations.json`, then warns about synthetic
  documents excluded from the file tree.
- The project analysis cache lives under `WEAVE_CACHE_DIR`, outside the source bundle.
- Generated files are skipped by default; `parse_generated: true` opts them in.
- External dependency documents use `_code/external/<language>/<qualified-name>`.
- The feature is registered as 0.8 / P1 in the roadmap.

## 17. Related Documents

- [Generic Blob Assets](blob-assets.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Weave Image Extension](weave-image.md)
- [Node Graph Engine](node-graph-engine.md)
- [Keyword + Fuzzy Search](keyword-fuzzy-search.md)
- [Node graph behavior](https://github.com/prulloac/weave/blob/main/docs/bdd/node-graph-engine.md)
- [Weave code behavior](https://github.com/prulloac/weave/blob/main/docs/bdd/weave-code.md)
- [Roadmap](../ROADMAP.md)
