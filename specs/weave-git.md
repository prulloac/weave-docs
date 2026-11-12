---
type: specification
title: "Weave Git Source Extension Specification"
description: "Source-provider contract for ingesting local or remote git repositories as commit-pinned snapshots with repository graph nodes and provenance."
tags:
  - "specification"
  - "git"
  - "extensions"
  - "source-provider"
  - "repository"
  - "0.9"
status: draft
generated:
  by: opencode/deepseek-v4.1-flash
---

# Specification: Weave Git Source Extension

## 1. Overview

`weave-git` is a source-provider extension. It turns a local or remote git repository into an
immutable snapshot that Weave can analyze with its existing Markdown and project analyzers.

```text
git URI + ref
    -> resolve commit
    -> fetch and cache
    -> materialize read-only snapshot
    -> core scans and analyzes the snapshot
    -> repository node + file, symbol and package nodes
```

The provider owns acquisition and provenance. It does not parse source code. `weave-code`, Markdown
parsing and future analyzers remain independent partner extensions.

## 2. Goals and Non-Goals

Goals:

- ingest a local repository or a remote git URI;
- resolve branches, tags and commits to a commit SHA;
- produce a reproducible snapshot and cache it outside the bundle;
- expose repository metadata as a first-class graph node;
- keep remote network access explicit and outside core defaults;
- work with any git host, including self-hosted servers;
- support incremental re-ingestion by commit;
- keep analyzers unchanged.

Non-goals:

- GitHub/GitLab/Bitbucket API enrichment;
- pull requests, issues, releases, wikis or CI history;
- a full commit-history graph in the first slice;
- executing repository code, hooks, build tools or package managers;
- automatic submodule recursion or Git LFS fetching by default;
- editing or pushing to the source repository;
- replacing `weave-code` language analysis;
- remote source discovery without an explicit URI.

## 3. Terminology

| Term | Meaning |
| --- | --- |
| Source provider | Extension role that resolves a URI into a local snapshot |
| Snapshot | Read-only materialized commit tree used for analysis |
| Repository node | Synthetic document representing the repository itself |
| Ref | Branch, tag, symbolic ref or commit requested by the operator |
| Commit | Resolved immutable git object ID |
| Worktree | Mutable local checkout, including uncommitted changes |
| Provenance | URI, ref, commit, path and provider metadata attached to ingested data |

## 4. Extension Role and Manifest

A source provider is discovered as `weave-<name>` and declares the provider role in its manifest:

```json
{
  "v": "weave.extension/v1",
  "name": "git",
  "source_providers": ["git"],
  "capabilities": ["repository", "ref-resolution"]
}
```

Rules:

- `source_providers` is an additive manifest field; existing manifests remain valid.
- The provider name matches the binary suffix, so `weave-git` declares `"name": "git"`.
- A provider supports one or more URI schemes. `weave-git` supports the schemes in §6.
- A binary may implement other roles in addition to source provision, but core invokes each role
  through its own contract.
- Provider output is bounded and validated by core before use.

## 5. Source Contract

### 5.1 Request

```json
{
  "v": "weave.source/v1",
  "type": "source_request",
  "uri": "git+https://git.example.com/team/weave.git",
  "ref": "main",
  "cache_dir": "/home/user/.cache/weave",
  "options": {
    "worktree": false,
    "submodules": false,
    "lfs": false,
    "depth": 1
  }
}
```

| Field | Meaning |
| --- | --- |
| `uri` | Canonical source URI or local path |
| `ref` | Branch, tag, symbolic ref or commit; defaults to the remote/default branch |
| `cache_dir` | Weave cache root from `WEAVE_CACHE_DIR`; never inside the bundle |
| `options.worktree` | Use a local mutable checkout instead of a commit snapshot |
| `options.submodules` | Follow submodules; default `false` |
| `options.lfs` | Fetch Git LFS objects; default `false` |
| `options.depth` | Fetch depth hint; `0` means provider default |

### 5.2 Response

```json
{
  "v": "weave.source/v1",
  "type": "source_response",
  "snapshot": {
    "path": "/home/user/.cache/weave/git/git.example.com/team/weave/8f3c2a1",
    "commit": "8f3c2a1d4b5e6f708192a3b4c5d6e7f8091a2b3c",
    "ref": "main",
    "uri": "https://git.example.com/team/weave.git",
    "read_only": true
  },
  "repository": {
    "id": "_repo",
    "name": "weave",
    "title": "Weave",
    "description": "Local-first related-document database for OKF bundles.",
    "readme": "README.md",
    "host": "git.example.com",
    "owner": "team",
    "license": "MIT"
  },
  "warnings": []
}
```

Rules:

- `snapshot.path` is an absolute path readable by core; core never writes it.
- `snapshot.commit` is a full commit SHA. A provider must not return a symbolic ref as the commit.
- `repository.id` is `_repo` for the source. Core scopes it by bundle/source root.
- `repository` fields are optional except `id` and `name`; absent values are omitted.
- `repository.description` follows §8.2.
- Unknown fields are ignored.
- A response that does not identify a commit is invalid.

### 5.3 Invocation order

1. Core resolves a source URI to a provider.
2. Core invokes the provider before asset discovery.
3. Core validates the snapshot path, commit and limits.
4. Core scans and analyzes the snapshot with the configured enrichers/analyzers.
5. Core persists documents, edges, repository metadata and source provenance in one transaction.

A provider failure fails the source write. In permissive mode the previous snapshot remains served
and the source becomes `degraded`.

## 6. Git URIs and Ref Resolution

### 6.1 Supported forms

| Form | Example |
| --- | --- |
| Canonical git+HTTPS | `git+https://host/owner/repo.git` |
| Canonical git+SSH | `git+ssh://git@host/owner/repo.git` |
| SCP-like SSH | `git@host:owner/repo.git` |
| File URI | `git+file:///srv/repos/weave.git` |
| Local path | `/home/user/src/weave` |

Plain `https://` or `ssh://` without `git+` remains a local path error unless the command explicitly
selects git via `--git`. This avoids treating ordinary URLs as filesystem paths.

### 6.2 Ref rules

- No `ref` means the remote `HEAD` or the local `HEAD`.
- Branches, tags and full or abbreviated commit SHAs are accepted.
- A provider resolves the ref to a full commit before materializing.
- Abbreviated SHAs must resolve unambiguously; otherwise ingestion fails.
- Re-ingesting the same commit is a no-op.
- `--worktree` on a local repository uses the current checkout and records the current `HEAD` plus a
  dirty flag. Remote worktree mode is invalid.

### 6.3 Offline behavior

- If the requested commit is already cached, ingestion succeeds without network.
- If a ref cannot be resolved but a previous resolved commit exists for that ref, the provider may
  reuse the cached commit with a warning in permissive mode.
- Strict mode fails when the ref cannot be resolved.
- No provider may silently fall back to a different branch.

## 7. Snapshot Cache

Snapshots live under `WEAVE_CACHE_DIR`, never inside the bundle or index database:

```text
$WEAVE_CACHE_DIR/git/<host>/<owner-or-path>/<repo>/<commit>/
```

Rules:

- The commit is the cache key. The same commit yields the same snapshot path.
- Materialized snapshots are read-only.
- Providers may keep a bare mirror and materialize trees from it.
- Symlinks must not escape the snapshot root; unsafe entries are skipped with a warning.
- A snapshot is safe to delete; core never treats it as durable source of truth.
- Cache cleanup is explicit or LRU-based; it never runs during a read.
- The provider returns the same path for the same commit so re-analysis can use the parse cache.

## 8. Repository Document

### 8.1 Identity and fields

Each git source produces one repository document:

| Field | Value |
| --- | --- |
| `id` | `_repo` |
| `doc_type` | `Repository` |
| `content_kind` | `blob` |
| `title` | README title → manifest name → repository directory name |
| `description` | §8.2 |
| `body` | Root README Markdown |
| `keywords` | repository name, README headings, topics, license, bounded to 64 |
| `content_metadata` | provider, URI, host, owner, name, ref, commit, readme path, license, worktree |

The repository node is synthetic and is not written back into the snapshot or bundle.

### 8.2 Description extraction

Deterministic order:

1. `description` in README frontmatter;
2. first non-heading, non-code-fence paragraph in the README;
3. description from a supported project manifest;
4. empty string.

No network call, hosting API or LLM is required. The existing Markdown fallback rule is reused.

### 8.3 README selection

- Root `README.md` or `README.markdown`, case-insensitive.
- Only the repository root README becomes the repository body.
- If no README exists, the repository node is still created with an empty body, a name-based title
  and one warning.
- `.rst`, `.txt` and generated README formats are deferred.

### 8.4 Provenance

Every file and symbol document produced from the snapshot carries:

- `repo_id: "_repo"`;
- `repo_uri`, `repo_ref` and `repo_commit`;
- bundle-relative `path`;
- analyzer name and parser status.

Provenance is metadata, not a substitute for stable graph identity.

## 9. Graph Model

### 9.1 Nodes

| Node | Meaning |
| --- | --- |
| `Repository` | The repository hub document |
| `File` | Source or documentation file |
| `Symbol` | Function, type, class, method or other declaration |
| `ExternalPackage` | Dependency referenced by a manifest or import |
| `Project` | Nested package in a monorepo (later slice) |

### 9.2 Edges

| Kind | From | To | Meaning |
| --- | --- | --- | --- |
| `contains` | repository or project | file or project | Structural containment |
| `declares` | file | symbol | Existing code declaration edge |
| `imports` | file | file or external package | Existing import edge |
| `references` | file or symbol | symbol or external package | Existing reference edge |
| `calls` | symbol | symbol or external package | Existing call edge |
| `inherits` | symbol | symbol or external package | Existing inheritance edge |
| `implements` | symbol | symbol or external package | Existing implementation edge |
| `depends_on` | project or repository | external package | Manifest dependency (later slice) |

Rules:

- `contains` is additive to `weave.contract/v1` and is traversable by default.
- Repository-to-file `contains` edges make the repository a navigation hub without changing the
  existing file and symbol relations.
- Duplicate edges collapse by `from`, `to` and kind.
- Single-reference external targets remain metadata; repeated external targets become documents.
- Cross-repository traversal remains out of scope for the first slice.

## 10. CLI and Workspace

### 10.1 Single source

```sh
weave ingest git+https://git.example.com/team/weave.git --ref main --with-enricher code --json
weave ingest /home/user/src/weave --git --ref HEAD --with-enricher code --json
weave ingest /home/user/src/weave --git --worktree --with-enricher code --json
```

- `--git` selects git handling for a local path.
- `--ref` accepts a branch, tag or commit.
- `--worktree` is valid only for local repositories.
- `--with-enricher` and `--with-embedder` keep their existing meaning.

### 10.2 Workspace manifest

Existing string paths remain valid. A source may also be an object:

```yaml
version: 1
sources:
  docs: ../weave-docs
  core:
    git: git+https://git.example.com/team/weave.git
    ref: main
  extensions:
    git: git+ssh://git@git.example.com/team/weave-code.git
    ref: v0.8.0
```

Rules:

- The string form is a local path.
- The object form requires `git`; `ref` is optional.
- Until this specification is stable, the string-only form in [Workspace and Source Registry](workspace.md)
  remains authoritative; the object form ships with slice G4.
- Aliases and duplicate-path validation remain unchanged.
- The same repository may not be registered under two aliases in one workspace.
- Workspace `ingest`, `rebuild` and `sync` resolve each git source before analysis.

### 10.3 Source registry and MCP

- `weave source list` and `weave source show` include `provider`, `uri`, `ref` and `commit`.
- `weave://workspace/sources` and the `weave_sources` MCP tool include the same provenance.
- The MCP server remains read-only and never fetches.
- `--watch` watches the manifest and cached snapshots; it does not poll remotes. A remote refresh is
  an explicit `weave sync`.

### 10.4 Source registry schema

The workspace source registry is extended in schema v9:

```sql
provider TEXT NOT NULL DEFAULT 'path',
uri TEXT NOT NULL DEFAULT '',
ref_name TEXT NOT NULL DEFAULT '',
metadata_json TEXT NOT NULL DEFAULT '{}'
```

`provider`, `uri` and `ref_name` are explicit because core uses them for source resolution, listing
and diagnostics. The resolved commit and provider-specific values live in versioned
`metadata_json`:

```json
{
  "v": 1,
  "commit_sha": "8f3c2a1d4b5e6f708192a3b4c5d6e7f8091a2b3c",
  "host": "git.example.com",
  "owner": "team",
  "name": "weave",
  "worktree": false,
  "default_branch": "main"
}
```

Rules:

- `path` remains the stable local snapshot root used as the bundle root.
- `metadata_json.commit_sha` is required for git sources and empty for path sources.
- Unknown metadata keys are preserved.
- Git sources validate `commit_sha` in Go; the database does not require a separate commit column.
- Metadata never contains credentials, tokens or full command output.
- Existing path sources backfill to `provider='path'`, `uri=<path>`, `ref_name=''` and
  `metadata_json='{}'`.
- Older binaries cannot open a v9 database; upgrading is one-way for the local index.

## 11. Security, Privacy and Limits

- Remote fetch is opt-in per source; core and MCP never fetch implicitly.
- Providers must not execute repository code, build tools, package managers or hooks.
- Providers must disable or ignore hooks, smudge/clean filters and submodule recursion by default.
- Submodules and Git LFS are opt-in.
- Credentials come from the operator's git configuration, SSH agent or provider environment; they
  are never written to the index, logs, warnings or envelopes.
- Providers must not log repository contents, tokens or full command output.
- The snapshot path must resolve inside the provider cache root.
- Reject symlinks that escape the snapshot root.
- Bound clone size, file count, individual file size, fetch time and snapshot depth.
- Default limits mirror the code-extension limits: 4 MiB per file, 512 MiB per project, 10,000 files.
- Binary files are recorded as metadata or skipped; they are not parsed as source.

## 12. Failure Handling

| Condition | Behavior |
| --- | --- |
| Provider missing | `EXTENSION_NOT_FOUND`; source is not indexed |
| Invalid URI | `INVALID_REQUEST` |
| Ref not found | `INVALID_REQUEST`; no fallback to another branch |
| Authentication failure | Provider error; no credentials in the message |
| Network timeout | Strict fails; permissive keeps the previous snapshot and marks `degraded` |
| Snapshot exceeds limits | Warning or failure per source mode; no partial graph |
| Unsafe symlink | Skip entry with a warning |
| Missing README | Repository node retained with empty body and one warning |
| Commit already cached | Reuse snapshot; skip re-fetch |
| Malformed provider response | `EXTENSION_PROTOCOL`; no partial write |
| Duplicate source alias or path | `WORKSPACE_INVALID` |

## 13. Testing

- Local repository, remote `file://` repository and fake HTTP/SSH provider fixtures.
- Branch, tag, full SHA and abbreviated SHA resolution.
- Commit pinning, cache reuse and offline reuse.
- Re-ingesting the same commit is a no-op.
- Ref update produces a new snapshot and transactionally replaces the previous graph.
- Repository node title and description from README frontmatter, first paragraph, manifest and
  fallback name.
- Missing README, non-GitHub remote and self-hosted host metadata.
- README body is searchable; source code is not parsed by the git provider.
- `contains` edges from repository to files are present and traversable.
- Workspace manifest object form, source registry provenance and MCP source resources.
- Submodules, LFS, symlink escape, size limits and credential redaction.
- Existing Markdown-only and local project behavior unchanged without a git source.
- Full gate, race suite and calibration unchanged.

## 14. Acceptance Criteria

1. A local or remote git URI can be ingested by explicit operator request.
2. Every ingestion resolves to a full commit and is reproducible from the cache.
3. The provider never writes into the bundle or index database.
4. `weave-git` only acquires and describes; it does not parse code or invoke `weave-code`.
5. The repository appears as a `Repository` node with README body, title, description and provenance.
6. Existing Markdown and project analyzers run unchanged on the snapshot.
7. Repository-to-file `contains` edges support navigation without changing existing relations.
8. Remote git hosts other than GitHub work through generic git.
9. Network, credentials, size and symlink policies are explicit and testable.
10. MCP serves git-backed sources read-only and never fetches.

## 15. Delivery Slices

| Slice | Scope |
| --- | --- |
| G1 | `weave.source/v1` contract, manifest role and local snapshot provider |
| G2 | Remote git fetch, commit resolution and cache |
| G3 | Repository node, README extraction, `contains` edges and provenance |
| G4 | Workspace object sources, source registry provenance and MCP resources |
| G5 | Incremental commit updates, dependency manifests and monorepo projects |
| G6 | Optional commit history and host-specific enrichments |

## 16. Resolved Decisions

- Git acquisition is a source-provider extension, not an enricher or project analyzer.
- `weave-git` and `weave-code` are partner extensions orchestrated by core.
- Commit-pinned snapshots are the default; worktree ingestion is explicit and local-only.
- The repository node ID is `_repo` and its body is the root README.
- Description extraction is deterministic: README frontmatter, first paragraph, manifest, empty.
- Generic git is authoritative; hosting APIs are optional later enrichments.
- The source registry keeps `provider`, `uri` and `ref_name` as explicit columns; `commit_sha` and
  provider-specific fields live in versioned `metadata_json`.
- The first slice ingests one snapshot per source and does not graph commit history.

## Related Documents

- [ADR 0011: Git Repositories as Source-Provider Extensions](../architecture/adr/0011-git-repositories-as-source-providers.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Workspace and Source Registry](workspace.md)
- [Weave Code Extension](weave-code.md)
- [Generic Blob Assets](blob-assets.md)
- [Weave Image Extension](weave-image.md)
