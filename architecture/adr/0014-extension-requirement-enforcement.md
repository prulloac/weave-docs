---
type: Architecture Decision Record
title: "ADR 0014: Extension Requirement Enforcement"
description: "Refuses to run extensions whose declared version requirements are unsatisfied, and makes installing such an extension an explicit error. Listing does not evaluate requirements."
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
fails later, or produces output that depends on behavior the installed core lacks. The earlier
[Extension Subprocess IPC §2.9](../../specs/extension-ipc.md) draft proposed a warning only. The owner
decided that unmet requirements must not be handled silently.

## Decision

1. **Selection is refused.** An extension with an unsatisfied `requires` entry is not invoked for any
   role. Selecting it fails the command before any write or search with `EXTENSION_REQUIREMENT_UNMET`.
2. **Installation is refused.** Installing an extension with unsatisfied requirements is an explicit
   error with a non-zero status. The staged file is discarded and any existing executable is left
   unchanged. Installers provide no flag to skip this check
   ([Extension Subprocess IPC §2.10](../../specs/extension-ipc.md)).
3. **No silent fallback.** A failed requirement is never downgraded to a warning, and the extension's
   role is not replaced by the core default.
4. **Versions are declared.** Manifests may declare `version`. A requirement on another extension is
   unsatisfied when that extension declares no version.
5. **Listing does not evaluate requirements.** `weave extensions list` keeps its directory-scan
   behavior and does not run any executable.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Warn only, as in the earlier draft | Rejected by the owner: a warning is easy to miss and the command still produces results from a mismatched extension |
| Refuse only when a requirement names `weave` | Rejected: companion-extension requirements have the same failure mode |
| Show requirement status in `extensions list` | Rejected by the owner: status requires running every discovered executable on list, including bundle-local ones in `.weave/bin`, which would be a trust change |
| Enforce only at selection, not at installation | Rejected: users would learn about an incompatible install only when a command fails |

## Consequences

- Installations that run an extension with an unmet requirement today will see that command fail after
  the upgrade. The failure is explicit and names the unmet entries, so the fix is to upgrade the core or
  the companion extension.
- Installers gain a step that runs `--describe --json` on a staged executable before placing it. This
  runs code from the download, which the installer already verifies against checksums.
- `weave extensions list` stays cheap and does not run extensions. Trust is unchanged for listing.
- The new code `EXTENSION_REQUIREMENT_UNMET` joins the error catalog. It is an additive error code in
  `weave.cli/v1`.
- The breaking nature of the change is a deliberate exception to the release-line policy in the backlog,
  which otherwise keeps breaking changes out of 0.X. Release notes must state it.

## Related Documents

- [Extension Subprocess IPC](../../specs/extension-ipc.md), §2.1, §2.9 and §2.10
- [ADR 0013: Role descriptor registry](0013-role-descriptor-registry.md)
- [ADR 0002: Config paths and additive machine output](0002-config-paths-and-db-location.md)
