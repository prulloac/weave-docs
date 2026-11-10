# Release Checklist

This checklist records the release state. Tag and publish steps are owner actions.

# v0.7.0 (current pre-1.0 release)

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

The rule and triage procedure are in
[1.0 Stability Gate and Issue Policy](specs/stability-gate.md).

## Notes

- 0.7 is a **pre-1.0** release. `weave.contract/v1` and `weave.cli/v1` remain authoritative and may
  still evolve in place until 1.0.0; after 1.0.0, breaking changes require a new contract major.
- The removed `v1.0.0` releases are not part of the upgrade path; users must install `v0.7.0`
  explicitly.
- `weave-image` requires `weave >= 0.7.0` and `weave-ai >= 0.7.0`.
- Publishing remains manual; a tag push only creates a draft release.
- The performance optimization program and watch event delivery are post-1.0 work.
