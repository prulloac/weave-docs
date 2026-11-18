---
type: Architecture Decision Record
title: "ADR 0014: Extension Requirement Enforcement"
description: "Refuses to load extensions whose declared version requirements are unsatisfied, reports them as errors in extension listings and never falls back silently."
tags:
  - "architecture"
  - "extensions"
  - "versioning"
  - "ipc"
status: proposed
---

# ADR 0014: Extension Requirement Enforcement

## Context

Extension manifests declare `requires` entries with a `min_version`, but core treats them as
informational. An extension that needs a newer `weave` or a newer companion extension runs anyway and
fails later, or produces output that depends on behavior the installed core lacks. [Extension Subprocess
IPC §2.9](../../specs/extension-ipc.md) previously proposed a warning only. The owner decided that
unmet requirements must not be handled silently.

## Decision

1. **Unsatisfied requirements block loading.** An extension with an unsatisfied `requires` entry is not
   invoked for any role. Selecting it fails the command before any write or search with
   `EXTENSION_REQUIREMENT_UNMET`.
2. **No silent fallback.** A failed requirement is never downgraded to a warning, and the extension's
   role is not replaced by the core default.
3. **Visible in listings.** `weave extensions list` shows a `status` of `ok` or `error` for every
   extension, with the error code and message. Errored extensions stay listed.
4. **Versions are declared.** Manifests may declare `version`. A requirement on another extension is
   unsatisfied when that extension declares no version.
5. **Listing reads manifests.** Listing runs `--describe --json` for each extension within the normal
   timeout. This is required to compute status.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Warn only, as in the earlier §2.9 draft | Rejected by the owner: a warning is easy to miss and the command still produces results from a mismatched extension |
| Refuse only when a requirement names `weave` | Rejected: companion-extension requirements have the same failure mode |
| Keep listing a pure directory scan and add status only to `check` | Rejected: users would not see the error where they look for extensions |
| Versioned protocol negotiation with fallback protocols | Out of scope: this decision covers version requirements only |

## Consequences

- Installations that run an extension with an unmet requirement today will see that command fail after
  the upgrade. The failure is explicit and names the unmet entries, so the fix is to upgrade the core or
  the companion extension.
- `weave extensions list` now executes each discovered extension. This is a trust change: a bundle-local
  executable in `.weave/bin` runs when the list is produced. The
  [trust gate](../../backlog.md) item in Tier 14 must be considered with this change.
- The new code `EXTENSION_REQUIREMENT_UNMET` joins the error catalog. It is an additive error code in
  `weave.cli/v1`.
- The breaking nature of the change is a deliberate exception to the release-line policy in the backlog,
  which otherwise keeps breaking changes out of 0.X. Release notes must state it.

## Related Documents

- [Extension Subprocess IPC](../../specs/extension-ipc.md), §2.1 and §2.9
- [ADR 0013: Role descriptor registry](0013-role-descriptor-registry.md)
- [ADR 0002: Config paths and additive machine output](0002-config-paths-and-db-location.md)
