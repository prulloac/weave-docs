# Release Checklist

This checklist records the release state. Tag and publish steps are owner actions.

# v0.10.0 (current pre-1.0 release)

## Complete

- [x] Tagged and pushed `v0.10.0`: `weave` (`5a959e0`).
- [x] Release workflow built six static archives plus checksums and created the draft release
  ([run 43542961187](https://github.com/prulloac/weave/actions/runs/43542961187)).
- [x] Downloaded and verified all six assets against `weave_0.10.0_checksums.txt`; the Linux `amd64`
  binary reports `weave v0.10.0 (contract 1)` and exposes `extensions list --short`.
- [x] Published `v0.10.0` and installed it with `scripts/install.sh --version v0.10.0`.
- [x] The 0.10 feature set adds `weave extensions list --short` for names-only output.
- [x] `weave`, specs, roadmap and backlog describe the 0.10 extension-list addition.

## Notes

- 0.10 is a **pre-1.0** release for `weave`. `weave.contract/v1` and `weave.cli/v1` remain
  authoritative and may still evolve in place until 1.0.0.
- `weave-git` remains at v0.9.0; other first-party members remain at v0.8.0. All are compatible with
  `weave v0.10.0`.
- Publishing remains manual; a tag push only creates a draft release.
- The performance optimization program and watch event delivery are post-1.0 work.

# v0.9.0 (previous pre-1.0 release)

## Complete

- [x] Tagged and pushed `v0.9.0`: `weave` (`6e7b0f9`) and `weave-git` (`d2d62e3`).
- [x] Release workflows built six static archives plus checksums for both products and created draft
  releases.
- [x] Downloaded and verified the Linux `amd64` assets and checksums: `weave v0.9.0 (contract 1)` and
  `weave-git v0.9.0 (weave.extension/v1)`.
- [x] Published in order: `weave`, then `weave-git`.
- [x] The 0.9 feature set adds git sources: `weave.source/v1`, stable commit-pinned snapshots, remote
  fetch with offline reuse, repository nodes, workspace/MCP provenance, limits and cache GC,
  submodule/LFS opt-ins, manifest projects/dependencies and opt-in commit history.
- [x] `weave`, `weave-git`, specs, roadmap and backlog describe the 0.9 git source set.
- [x] Other first-party members remain at v0.8.0; their `weave >= 0.8.0` floors are satisfied by
  `weave v0.9.0`.

## 1.0 stability window

- [x] Window still started on **2026-11-10**, the date `v0.7.0` was published.
- [x] Earliest possible `v1.0.0`: **2026-12-10**.
- [x] Confirmed defects declared since the window started: **none**.
- [ ] No `confirmed-defect` issue remains open on the evaluation date.
- [ ] 30 consecutive days completed without a defect reset.

The rule and triage procedure are in
[1.0 Stability Gate and Issue Policy](specs/stability-gate.md).

## Notes

- 0.9 is a **pre-1.0** release for `weave` and `weave-git`. `weave.contract/v1` and `weave.cli/v1`
  remain authoritative and may still evolve in place until 1.0.0.
- `weave-git` is the first source-provider extension and works with `weave v0.9.0`.
- Publishing remains manual; a tag push only creates a draft release.
- The performance optimization program and watch event delivery are post-1.0 work.

# v0.8.0 (previous pre-1.0 release)

## Complete

- [x] Product versioning moved to `0.8.0` for `weave`, `weave-ai`, `weave-code`,
  `weave-codec-lz4`, `weave-image` and `weave-skills`.
- [x] Version floors aligned: `weave-image` requires `weave >= 0.8.0` and `weave-ai >= 0.8.0`;
  `weave-ai` vision/embeddings require `weave >= 0.8.0`; the agent skill targets `weave >= 0.8.0`.
- [x] Tagged `v0.8.0` and pushed: `weave-ai` (`5ef4b89`), `weave-codec-lz4` (`af34cc4`),
  `weave` (`077dc5d`), `weave-code` (`fe28aec`), `weave-image` (`bdd429e`),
  `weave-skills` (`4708eb9`).
- [x] Release workflows built six static archives plus checksums for each Go product and created
  draft releases; every workflow passed, including the core artifact smoke matrix.
- [x] Published `v0.8.0` in order: `weave-ai`, `weave-codec-lz4`, `weave`, `weave-code`,
  `weave-image`, then `weave-skills`.
- [x] Downloaded and ran the Linux `amd64` binaries: `weave`, `weave-ai`, `weave-code`,
  `weave-codec-lz4` and `weave-image` report `v0.8.0`.
- [x] The 0.8 feature set adds code knowledge: project analysis, eleven languages, code relations,
  optional symbols, external documents, `_code` raw export, ignore rules and resource limits.
- [x] Roadmap, backlog, specs, architecture, READMEs and compatibility metadata describe 0.8 and no
  longer present 0.7 as the current release.

## Notes

- 0.8 is a **pre-1.0** release. `weave.contract/v1` and `weave.cli/v1` remain authoritative and may
  still evolve in place until 1.0.0; after 1.0.0, breaking changes require a new contract major.
- `weave-code` requires a `weave` binary with project analysis (`>= 0.8.0`).
- `weave-image` requires `weave >= 0.8.0` and `weave-ai >= 0.8.0`.
- Publishing remains manual; a tag push only creates a draft release.
- The performance optimization program and watch event delivery are post-1.0 work.

# v0.7.0 (previous pre-1.0 release)

## Complete

- [x] Product versioning moved to `0.7.0` for `weave`, `weave-ai`, `weave-codec-lz4`,
  `weave-image` and `weave-skills`.
- [x] Version floors aligned: `weave-image` requires `weave >= 0.7.0` and `weave-ai >= 0.7.0`;
  `weave-ai` vision/embeddings require `weave >= 0.7.0`; the agent skill targets `weave >= 0.7.0`.
- [x] Removed the published `v1.0.0` releases and tags from all four Go product repositories.
- [x] Tagged `v0.7.0` and pushed: `weave-ai` (`5d41d58`), `weave-codec-lz4` (`185cc0b`),
  `weave` (`a54f883`), `weave-image` (`a5bf00f`), `weave-skills` (`b18dcdb`).
- [x] Release workflows built six static archives plus checksums for each Go product and created
  draft releases; all four workflows passed.
- [x] Published `v0.7.0` in order: `weave-ai`, `weave-codec-lz4`, `weave`, `weave-image`.
- [x] Published the `weave-skills` `v0.7.0` tag and release.
- [x] Downloaded and ran the Linux `amd64` binaries: `weave` reports `v0.7.0`,
  `weave-ai`, `weave-codec-lz4` and `weave-image` report `v0.7.0`.
- [x] The 0.7 feature set includes pluggable scoring, extension data, workspaces, blob assets,
  codec extensions, embeddings and semantic search.
- [x] Roadmap, backlog, specs, architecture, READMEs and installation docs describe 0.7 and no
  longer claim a 1.0 GA.

## 1.0 stability window

- [x] Window started on **2026-11-10**, the date `v0.7.0` was published.
- [x] Earliest possible `v1.0.0`: **2026-12-10**.
- [x] Confirmed defects declared since the window started: **none**.
- [ ] No `confirmed-defect` issue remains open on the evaluation date.
- [ ] 30 consecutive days completed without a defect reset.

## Notes

- 0.7 is a **pre-1.0** release. `weave.contract/v1` and `weave.cli/v1` remain authoritative and may
  still evolve in place until 1.0.0; after 1.0.0, breaking changes require a new contract major.
- The removed `v1.0.0` releases are not part of the upgrade path; users must install `v0.7.0`
  explicitly.
- `weave-image` requires `weave >= 0.7.0` and `weave-ai >= 0.7.0`.
- Publishing remains manual; a tag push only creates a draft release.
- The performance optimization program and watch event delivery are post-1.0 work.
