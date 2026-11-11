# Release Checklist

This checklist records the release state. Tag and publish steps are owner actions.

# v0.8.0 (current pre-1.0 release)

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

## 1.0 stability window

- [x] Window still started on **2026-11-10**, the date `v0.7.0` was published.
- [x] Earliest possible `v1.0.0`: **2026-12-10**.
- [x] Confirmed defects declared since the window started: **none**.
- [ ] No `confirmed-defect` issue remains open on the evaluation date.
- [ ] 30 consecutive days completed without a defect reset.

The rule and triage procedure are in
[1.0 Stability Gate and Issue Policy](specs/stability-gate.md).

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
