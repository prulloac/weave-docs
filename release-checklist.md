# Release Checklist

This checklist records the release state. Tag and publish steps are owner actions. Sections are
newest first.

# v1.1.0

## Complete

- [x] ADR 0004, 0005 and 0006 accepted; media and embedding specs/BDD approved.
- [x] `weave-ai` vision and embedding requests, provider payloads, 32 MiB stdin and 20 MiB image cap
  covered by tests.
- [x] Core schema v7 body split: text bodies stay raw, binary bodies use `body_compressed` with zstd
  by default.
- [x] Blob ingestion and retrieval, MCP blob resources and raw export implemented and tested.
- [x] Codec extension resolution, manifest validation and round-trip tests implemented.
- [x] Durable embeddings with per-space `vec0`, semantic search, audit findings and re-embedding
  implemented and tested.
- [x] Enrichment persists title, description, text, metadata and warnings; extension warnings are
  counted without discarding local metadata.
- [x] `weave-image` v0.1.0 repository with OCR, EXIF, dimensions, `weave-ai` vision, best-effort
  fallbacks, installers, CI and tests.
- [x] `weave-codec-lz4` v0.1.0 repository with the raw codec protocol, manifest, installers, CI and
  tests.
- [x] Real vision validated with `weave-ai` and Ollama `qwen2.5vl:3b`; title and description stored
  with zero warnings.
- [x] Real embeddings validated with Ollama `embeddinggemma-2:latest`; semantic search returned the
  expected document.
- [x] Release dry run built six static targets and verified checksums for `weave-ai`,
  `weave-codec-lz4`, `weave` and `weave-image`.
- [x] Installers validated for published `weave` and `weave-ai` v1.0.0 (shell and PowerShell);
  `weave-image` and `weave-codec-lz4` installers validated against local release-base overrides.
- [x] Repository gates pass locally: `weave`, `weave-image` and `weave-codec-lz4` `verify.sh`.
- [x] CI on `main` passed: `weave` (`41955463857`), `weave-image` (`41955463694`),
  `weave-codec-lz4` (`41955463584`).

## Owner steps

- [ ] Decide the final versions: `weave-ai v1.1.0`, `weave-codec-lz4 v0.1.0`, `weave v1.1.0`,
  `weave-image v0.1.0`.
- [ ] Tag and push in order: `weave-ai`, `weave-codec-lz4`, `weave`, `weave-image`.
- [ ] Review each draft release, then publish manually with
  `gh release edit <tag> --draft=false`.
- [ ] After `weave-ai v1.1.0` is published, run the `weave-image` installer without `--no-ai` to
  exercise the automatic `weave-ai >= 1.1.0` dependency install.
- [ ] Verify all four installers against the published assets on Linux and Windows.

## Notes

- `weave-image` requires `weave >= 1.1.0` and `weave-ai >= 1.1.0`, so `weave-ai` must be published
  first.
- `weave-codec-lz4` has no dependency on the other releases; publishing it before core keeps the
  documented release order and lets core v1.1.0 advertise it from day one.
- Publishing remains manual; a tag push only creates a draft release.
- No v1.1.0 tags exist yet.

# v1.0.0

## Complete

- [x] Feature register shipped, with optimization marked post-GA stretch.
- [x] MIT license added and included in release archives.
- [x] Documentation gate: `docs-lint` passes with 0 violations.
- [x] Markdown lint: 0 issues.
- [x] Regression gate: shuffled race suite, vet, staticcheck, govulncheck, fuzzing and built-binary
  smoke.
- [x] CI on `main`: run `41225010841` passed.
- [x] Release dry run `v1.0.0-rc.3`: run `41225227470` passed on Linux, macOS and Windows.
- [x] Dry run produced all six archives, checksums and build info without creating a release.
- [x] Linux archive inspected: `weave`, `README.md`, `LICENSE`.
- [x] Published `v1.0.0` for `weave` and `weave-ai` with six static archives each.
- [x] User-level installers verified on Linux and Windows against the published assets.

## Owner steps

- [x] Decide the final version: `v1.0.0`.
- [x] Create an annotated tag:
      `git tag -a v1.0.0 -m "Weave v1.0.0"`.
- [x] Push the tag: `git push origin v1.0.0`.
- [x] Watch the release workflow. It verifies, builds the matrix, runs artifact smoke and creates a
      **draft** release.
- [x] Review the draft: notes, six archives, checksums and build info.
- [x] Publish manually with `gh release edit v1.0.0 --draft=false`.
- [x] Verify the user-level installers against the published release into a temporary HOME with
      `--bin-dir ... --no-modify-path` and the PowerShell equivalent.

## Notes

- Publishing is intentionally manual; a tag push never publishes directly.
- If the draft is wrong, delete it and re-run after fixing the cause. The workflow refuses to
  overwrite an existing release.
- The performance optimization program is a post-GA stretch goal and does not block this tag.
