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
status: stable
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
  "source_id": "w8f3c2a1d4b5e6f7",
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
| `source_id` | Stable source identity derived by core; excludes ref and commit |
| `uri` | Canonical source URI or local path |
| `ref` | Branch, tag, symbolic ref or commit; defaults to the remote/default branch |
| `cache_dir` | Weave cache root from `WEAVE_CACHE_DIR`; never inside the bundle |
| `options.worktree` | Use a local mutable checkout instead of a commit snapshot |
| `options.submodules` | Follow submodules; default `false` |
| `options.lfs` | Fetch Git LFS objects; default `false` |
| `options.depth` | Fetch depth hint; `0` means provider default |
| `options.permissive` | Allow cached-commit reuse when a remote ref cannot be resolved |

### 5.2 Response

```json
{
  "v": "weave.source/v1",
  "type": "source_response",
  "snapshot": {
    "path": "/home/user/.cache/weave/sources/w8f3c2a1d4b5e6f7/worktree",
    "source_id": "w8f3c2a1d4b5e6f7",
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
- `snapshot.path` is the stable bundle root for the source. It must not change when only the commit
  changes.
- `snapshot.source_id` must match the request.
- `snapshot.commit` is a full commit SHA. A provider must not return a symbolic ref as the commit.
- `repository.id` is `_repo` for the source. Core scopes it by bundle/source root.
- `repository` fields are optional except `id` and `name`; absent values are omitted.
- `repository.description` follows §8.2.
- Unknown fields are ignored.
- A response that does not identify a commit is invalid.

### 5.3 Invocation order

1. Core resolves a source URI to a provider.
2. Core computes a stable `source_id` from the workspace/source identity and canonical URI.
3. Core invokes the provider before asset discovery.
4. Core validates the snapshot path, commit and limits.
5. Core scans and analyzes the snapshot with the configured enrichers/analyzers.
6. Core persists documents, edges, repository metadata and source provenance in one transaction.

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
selects git via `--git`. This avoids treating ordinary URLs as filesystem paths. Once the git
provider is explicitly selected, plain remote URLs are accepted. Password and token userinfo is
stripped before the URI is returned or persisted.

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

### 6.4 Git backend

`weave-git` uses the operator's system `git` as its backend. The provider starts a bare mirror with
`git init --bare`, fetches with `git fetch`, resolves commits with `git rev-parse` and exports trees
with `git archive`. Authentication therefore follows the operator's git configuration, credential
helpers and SSH agent; `GIT_TERMINAL_PROMPT=0` prevents interactive prompts from hanging ingestion.

A pure-Go `go-git` backend remains deferred. It would avoid the external binary, but it would change
credential-helper, transport and protocol support. A hybrid backend may be revisited only through a
new decision; the `weave.source/v1` contract is backend-neutral.

## 7. Snapshot Cache and Stable Identity

The stable unit is **source identity**, not commit identity. Core computes `source_id` from the
workspace/source identity and the canonical URI. The ref and commit are mutable state.

Cache layout:

```text
$WEAVE_CACHE_DIR/sources/<source_id>/worktree
$WEAVE_CACHE_DIR/sources/<source_id>/state.json
$WEAVE_CACHE_DIR/git/<host>/<owner-or-path>/<repo>.git
```

`worktree` is a real directory and the stable bundle root. The bare mirror stores git objects. File
URIs use `_` as the host and owner segment when the URI has no host or owner.

### 7.1 Source identity

- Workspace source: `source_id = hash(workspace root + alias + canonical URI)`.
- Single-source ingest: `source_id = hash(canonical URI)`.
- `source_id` excludes the ref and commit.
- Changing a branch or tag reuses the same `worktree` and bundle root.
- Changing the canonical URI under the same alias creates a new `source_id`; old rows are pruned
  explicitly or by source removal.
- Two aliases may target different refs because the alias is part of the workspace identity.

### 7.2 Materialization

1. Resolve the requested ref to a full commit.
2. Fetch into the bare mirror when needed.
3. Export the commit tree into `worktree.stage-<pid>`.
4. Validate file count, size, symlinks and other limits in the staging tree.
5. Under the provider lock, swap the staging tree into place:
   `worktree -> worktree.old`, `worktree.stage-<pid> -> worktree`, then remove `worktree.old`.
6. Write `state.json` atomically with the new commit, ref and timestamp.
7. Return `snapshot.path = worktree` and `snapshot.commit`.

Core scans only after the provider returns successfully. The single-writer lock prevents another
writer from changing the tree during ingestion. A failure before the swap leaves the old worktree
valid; a failure during the swap is repaired on the next provider run from the bare mirror and
`state.json`.

The default path uses `git archive`, so hooks, smudge filters, submodule recursion and network LFS
are inert. When `options.submodules` or `options.lfs` is enabled, the provider clones the resolved
commit into a temporary checkout under the cache, disables hooks, runs submodule update or
`git lfs pull`, validates the same limits, strips every `.git` entry and only then swaps the tree.

### 7.3 Why a real worktree, not a symlink

A `current -> objects/<commit>` symlink would look cleaner, but Weave's asset scanner uses
`filepath.WalkDir` on the bundle root, and `WalkDir` does not follow a symlink root. A symlink bundle
root would be treated as a non-directory entry instead of being traversed.

The provider therefore materializes a real `worktree` directory. This keeps existing scanning, sync,
watchers and parse caching working without a core-wide symlink resolution rule.

### 7.4 Rules

- `worktree` is owned by the provider and read-only to core.
- The worktree contains no `.git` metadata, hooks or submodule checkouts by default.
- Re-ingesting the same commit is a no-op.
- Changing ref or commit updates `state.json` and replaces the graph under the same bundle root.
- Cache cleanup never deletes a worktree referenced by an active source.
- Old git objects are pruned by an explicit GC pass, never during a read.
- Metadata and state files never contain credentials or full command output.

### 7.5 Cache maintenance

`weave-git gc` performs explicit cache maintenance:

- remove `worktree.stage-*` and `worktree.old` leftovers;
- remove source directories without a valid `state.json` or `worktree`;
- with one or more `--keep <source_id>`, treat that set as authoritative and remove other source
  directories;
- run `git gc --prune=now` on bare mirrors and retain the mirror itself;
- support `--dry-run` and `--json` for orchestration.

Active worktrees are identified by `state.json` and are never removed unless the `--keep` set
excludes them. The command never touches the bundle or index database.

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
| `Project` | Nested package in a monorepo |
| `ExternalPackage` | Dependency referenced by a manifest or import |

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
| `depends_on` | project | external package | Manifest dependency |

Rules:

- `contains` is additive to `weave.contract/v1` and is traversable by default.
- Repository-to-file `contains` edges make the repository a navigation hub without changing the
  existing file and symbol relations.
- Duplicate edges collapse by `from`, `to` and kind.
- Single-reference analyzer-imported external targets remain metadata; repeated external targets
  become documents. Declared manifest dependencies are always materialized (§9.3).
- Cross-repository traversal remains out of scope for the first slice.

### 9.3 Projects and dependencies

The source provider discovers project manifests in the materialized snapshot. Supported manifests:

| Manifest | Ecosystem | Declared dependencies |
| --- | --- | --- |
| `go.mod` | `go` | `require` directives, including `// indirect` |
| `package.json` | `npm` | `dependencies`, `devDependencies`, `peerDependencies`, `optionalDependencies` |
| `Cargo.toml` | `cargo` | `dependencies`, `dev-dependencies`, `build-dependencies` |
| `pyproject.toml` | `python` | `project.dependencies`, `project.optional-dependencies` |

Rules:

- A project root is a directory containing one supported manifest. If several are present, the
  provider selects one by the order in the table and reports a warning.
- The repository root project uses ID `_project`; a nested project uses
  `_project/<bundle-relative directory>`.
- Project documents have type `Project`, content kind `symbol`, a title and name from the manifest,
  a description when declared, and `content_metadata` with `manifest`, `path`, `ecosystem`,
  `name` and dependency counts.
- The repository contains every project. A project contains the files under its directory; when
  projects nest, the deepest project owns the file. The repository retains its existing file
  `contains` edges for compatibility.
- Every declared dependency becomes an `ExternalPackage` document with ID
  `_package/<ecosystem>/<slug>`. Slug is the lowercased dependency name with non-alphanumeric
  characters collapsed to `-`. Versions and scopes (`runtime`, `development`, `build`, `peer`,
  `optional`, `indirect`) are aggregated in `content_metadata`.
- A `depends_on` edge links each project to each declared dependency. `depends_on` is additive to
  `weave.contract/v1` and traversable by default.
- Discovery skips `.git`, `node_modules`, `vendor`, `target`, `dist`, `build` and `.venv`.
- Discovery is bounded: 1 MiB per manifest, 128 projects and 2,000 dependencies per source.
- Repository description falls back to the root manifest description when the README has none.

Provider responses carry the discovered projects and dependencies. Core validates and materializes
the synthetic `Project` and `ExternalPackage` documents; analyzers are unchanged.

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
metadata_json TEXT NOT NULL DEFAULT '{}'
```

`path` remains the stable local snapshot root used as the bundle root. `provider` is the source
resolution router (`path`, `git`, future providers). Provider-specific provenance lives in versioned
`metadata_json`:

```json
{
  "v": 1,
  "uri": "git+https://git.example.com/team/weave.git",
  "ref_name": "main",
  "commit_sha": "8f3c2a1d4b5e6f708192a3b4c5d6e7f8091a2b3c",
  "host": "git.example.com",
  "owner": "team",
  "name": "weave",
  "worktree": false,
  "default_branch": "main"
}
```

Rules:

- `path` is the only explicit source locator; do not store a duplicate `uri` column.
- For path sources, `uri` is derived from `path`; `metadata_json` may be empty.
- `metadata_json.commit_sha` is required for git sources and empty for path sources.
- `weave source list` and `weave source show` decode or derive `provider`, `uri`, `ref` and `commit`
  for their output.
- Unknown metadata keys are preserved.
- Git sources validate `commit_sha`, `uri` and `ref_name` in Go; the database does not require
  separate columns.
- Metadata never contains credentials, tokens or full command output.
- Existing path sources backfill to `provider='path'` and `metadata_json='{}'`.
- Older binaries cannot open a v9 database; upgrading is one-way for the local index.

## 11. Security, Privacy and Limits

- Remote fetch is opt-in per source; core and MCP never fetch implicitly.
- Providers must not execute repository code, build tools, package managers or hooks.
- Providers must disable or ignore hooks, smudge/clean filters and submodule recursion by default.
- Submodules and Git LFS are opt-in. Submodules are skipped by default and are only materialized
  with `options.submodules`; LFS pointers are only expanded with `options.lfs` and `git-lfs`
  installed. Missing `git-lfs` produces a warning, not a partial failure.
- Opt-in checkout mode clones under the provider cache, disables hooks, then removes all git
  metadata before the snapshot becomes visible to core.
- Credentials come from the operator's git configuration, SSH agent or provider environment; they
  are never written to the index, logs, warnings or envelopes.
- Providers must not log repository contents, tokens or full command output.
- The snapshot path must resolve inside the provider cache root.
- Reject symlinks that escape the snapshot root.
- Bound clone size, file count, individual file size, fetch time and snapshot depth.
- Default limits mirror the code-extension limits: 4 MiB per file, 512 MiB per project, 10,000 files.
  The provider enforces them while extracting the archive, before the worktree swap.
- Cache maintenance is explicit through `weave-git gc`; it never runs during a read or ingest.
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
- A ref or commit update replaces the graph under the same stable bundle root.
- The worktree is a real directory and remains the same across commit updates.
- Ref changes update `state.json` and provenance without changing the bundle root.
- Repository node title and description from README frontmatter, first paragraph, manifest and
  fallback name.
- Missing README, non-GitHub remote and self-hosted host metadata.
- README body is searchable; source code is not parsed by the git provider.
- `contains` edges from repository to files are present and traversable.
- Root manifest descriptions feed the repository description fallback.
- Manifest projects and dependencies produce stable `Project`, `ExternalPackage` and `depends_on`
  graph data.
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
11. Commit updates keep the same bundle root; no stale source roots accumulate.
12. Manifests produce deterministic `Project` and `ExternalPackage` nodes with `depends_on` edges.

## 15. Delivery Slices

| Slice | Scope |
| --- | --- |
| G1 | `weave.source/v1` contract, manifest role and local snapshot provider |
| G2 | Remote git fetch, commit resolution and cache |
| G2b | Snapshot limits and explicit cache garbage collection |
| G2c | Submodule and Git LFS opt-ins |
| G3 | Repository node, README extraction, `contains` edges and provenance |
| G4 | Workspace object sources, source registry provenance and MCP resources |
| G5 | Incremental commit updates, dependency manifests and monorepo projects |
| G5a | Manifest discovery, `Project` nodes, `ExternalPackage` nodes and `depends_on` edges |
| G6 | Optional commit history and host-specific enrichments |

## 16. Resolved Decisions

- Git acquisition is a source-provider extension, not an enricher or project analyzer.
- `weave-git` and `weave-code` are partner extensions orchestrated by core.
- Commit-pinned snapshots are the default; worktree ingestion is explicit and local-only.
- The stable unit is source identity, not commit identity: `source_id` excludes ref and commit.
- The stable bundle root is a real `worktree` directory under `WEAVE_CACHE_DIR`; a symlink bundle
  root is rejected because core scanning uses `filepath.WalkDir`.
- Commit updates swap worktree contents under the same bundle root.
- The repository node ID is `_repo` and its body is the root README.
- Description extraction is deterministic: README frontmatter, first paragraph, manifest, empty.
- Generic git is authoritative; hosting APIs are optional later enrichments.
- The source registry keeps only `provider` as the explicit provenance column; `uri`, `ref_name`,
  `commit_sha` and provider-specific fields live in versioned `metadata_json`.
- The first slice ingests one snapshot per source and does not graph commit history.

## Related Documents

- [ADR 0011: Git Repositories as Source-Provider Extensions](../architecture/adr/0011-git-repositories-as-source-providers.md)
- [Extension Subprocess IPC](extension-ipc.md)
- [Workspace and Source Registry](workspace.md)
- [Weave Code Extension](weave-code.md)
- [Generic Blob Assets](blob-assets.md)
- [Weave Image Extension](weave-image.md)
