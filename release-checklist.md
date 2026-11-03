# v1.0.0 Release Checklist

This checklist records the release state. The tag and publish steps are owner actions.

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
