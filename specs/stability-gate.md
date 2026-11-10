---
type: specification
title: "1.0 Stability Gate and Issue Policy"
description: "Defines the 30-day defect-free window, the supported community issue types and the triage procedure that decides when Weave may release 1.0.0."
tags:
  - "specification"
  - "release"
  - "stability"
  - "issues"
status: stable
generated:
  by: opencode/deepseek-v4.1-flash
---

# Specification: 1.0 Stability Gate and Issue Policy

## 1. Overview

Weave is pre-1.0. 1.0.0 is a stability claim, not a feature release. This specification defines the
gate that opens it, the issue types the project accepts from the community, and the triage process
that turns a report into a confirmed defect or a closed report.

The gate is intentionally narrow: **one month on `main` without a declared defect**.

## 2. Stability Gate

1.0.0 may be released only when both conditions hold:

1. At least **30 consecutive calendar days** have passed since the start of the current stability
   window, or since the most recent declared defect, whichever is later.
2. At the evaluation date there is **no open issue labeled `confirmed-defect`** in
   `prulloac/weave` that was declared against `main` or the latest published release.

Rules:

- A **declared defect** is an issue to which a maintainer applies the `confirmed-defect` label. The
  label is the declaration; the report text alone is not.
- A `regression` is a declared defect and resets the window.
- A confirmed **security defect** resets the window even when it is tracked privately through a
  GitHub security advisory.
- Reports closed as `duplicate`, `invalid`, `wontfix`, `needs-repro` or `question` do not reset the
  window.
- A defect in a third-party extension, or in an extension repository's own code that Weave does not
  ship, does not reset the window. Defects in first-party products (`weave`, `weave-ai`,
  `weave-codec-lz4`, `weave-image`, `weave-skills`) do.
- Fixing a confirmed defect resets the window start to the date the fix lands on `main`; the
  evaluation date must then be at least 30 days later.
- The window start and every reset are recorded in
  [release-checklist.md](../release-checklist.md) and on the pinned stability-gate issue in
  `prulloac/weave`.

The current window starts on **2026-11-10**, the date `v0.7.0` was published. The earliest possible
1.0.0 date is therefore **2026-12-10**, provided no defect is declared in between.

## 3. Supported Issue Types

Only `prulloac/weave` accepts issues. Every other Weave repository has issues disabled and points
reporters here.

Accepted:

| Type | Definition | Template |
| --- | --- | --- |
| Defect | Reproducible mismatch with a specification, documented behavior or release claim | `bug_report.yml` |
| Regression | Behavior that worked in a published release and fails on `main` or a later release | `bug_report.yml` |
| Documentation defect | Wrong, missing or contradictory documentation in `weave` or `weave-docs` | `docs_defect.yml` |
| Packaging or install defect | Installer, archive, checksum or version-floor failure | `bug_report.yml` |
| Security defect | Vulnerability or privacy leak | Private advisory only |

Not accepted as issues:

- Usage and configuration questions; consult the README and `docs/`.
- Feature requests and roadmap proposals; these are owner decisions tracked in `weave-docs`.
- Third-party extension bugs; report them to the extension maintainer.
- Reports without a reproducible command, bundle shape or environment.
- Duplicate reports.

## 4. Required Report Content

A defect report must include:

- Product and version (`weave version --json`, or the extension `--version` output).
- Commit (`main`) or release tag under test.
- OS, architecture and install method (archive, installer or `go install`).
- Exact command and flags.
- Expected behavior and a link to the owning spec or documentation.
- Actual behavior, exit code and the relevant stderr.
- A minimal bundle or fixture shape; do not attach secrets or private content.

Reports missing this information receive `needs-repro` and may be closed after 14 days without a
response.

## 5. Triage Procedure

1. **Intake (0–3 business days).** A maintainer reads every new issue and applies one product label
   (`product/weave`, `product/weave-ai`, `product/weave-codec-lz4`, `product/weave-image`,
   `product/weave-skills` or `product/weave-docs`) plus `needs-repro` when content is missing.
2. **Reproduce (within 7 days).** The maintainer reproduces against `main` or the reported release.
   Success applies `confirmed-defect` and a severity label; failure with missing information keeps
   `needs-repro`.
3. **Classify.** Apply `regression`, `docs-defect`, `packaging`, or `security` as applicable.
4. **Close unsupported reports.** Apply `invalid`, `wontfix`, `question` or `duplicate` with a short
   explanation and a pointer to the accepted route.
5. **Fix.** A confirmed defect gets a failing test first, then a fix, then the full verification
   gate. The fixing PR references the issue.
6. **Declare the reset.** When the fix lands on `main`, record the date in the release checklist and
   the pinned stability-gate issue. The 30-day window restarts.
7. **Verify closure.** Close the issue only after the fix is on `main` and the report has a
   confirming test or release note.

Severity:

| Severity | Examples | Target |
| --- | --- | --- |
| `P1` | Data loss, privacy leak, security defect, install failure, regression | Fix before the next release; resets the window |
| `P2` | Wrong search/audit/export behavior with a workaround | Fix in the next release |
| `P3` | Documentation, diagnostics, cosmetic packaging | Batch with the next docs or release pass |

## 6. Repository Settings

- `prulloac/weave` keeps issues enabled, with issue templates and a blank-issue ban.
- `prulloac/weave-ai`, `prulloac/weave-codec-lz4`, `prulloac/weave-image`,
  `prulloac/weave-skills` and `prulloac/weave-docs` disable issues and link to the Weave issue
  chooser.
- Security reports use GitHub private vulnerability reporting, never a public issue.

## 7. Acceptance Criteria

1. The 30-day rule, reset conditions and evaluation date are documented and unambiguous.
2. Supported and unsupported issue types are listed with required content.
3. Triage states, labels, timelines and severity targets are documented.
4. Only `prulloac/weave` accepts issues; every other repository disables them and links here.
5. Issue templates collect the required report content.
6. The current window start is recorded in the release checklist and on a pinned issue.

## 8. Related Documents

- [Roadmap](../ROADMAP.md)
- [Release checklist](../release-checklist.md)
- [Release readiness](release-readiness.md)
- [ADR 0009](../architecture/adr/0009-product-versioning-0.7-pre-1.0.md)
- [Contributing](https://github.com/prulloac/weave/blob/main/CONTRIBUTING.md)
