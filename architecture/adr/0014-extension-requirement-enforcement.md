---
type: Architecture Decision Record
title: "ADR 0014: Extension Requirement Enforcement"
description: "Refuses to run extensions whose declared version requirements are unsatisfied, with an explicit error. Listing does not evaluate requirements. Installation rules are deferred for discussion."
tags:
  - "architecture"
  - "extensions"
  - "versioning"
  - "ipc"
status: accepted
---

# ADR 0014: Extension Requirement Enforcement

## Context

Extension manifests declare `requires` entries with a `min_version`, but core treats them as
informational. An extension that needs a newer `weave` or a newer companion extension runs anyway and
fails later, or produces output that depends on behavior the installed core lacks. The earlier
[Extension Subprocess IPC §2.9](../../specs/extension-ipc.md) draft proposed a warning only. The owner
decided that unmet requirements must not be handled silently.

`weave` has no extension install step today. The installers in this repository place only the `weave`
binary, so there is no moment in the current product at which an extension is installed by `weave`.

## Decision

1. **Selection is refused.** An extension with an unsatisfied `requires` entry is not invoked for any
   role. Selecting it fails the command before any write or search with `EXTENSION_REQUIREMENT_UNMET`,
   with exit status `1`, `EXTENSION_REQUIREMENT_UNMET` and the unmet entries in the message, as
   [extension IPC §2.9](../../specs/extension-ipc.md) and §5 define.
2. **No silent fallback.** A failed requirement is never downgraded to a warning, and the extension's
   role is not replaced by the core default.
3. **Versions are declared.** Manifests may declare `version`. A requirement on another extension is
   unsatisfied when that extension declares no version.
4. **Listing does not evaluate requirements.** `weave extensions list` keeps its directory-scan
   behavior and does not run any executable.

5. **Conformance check.** `weave extensions check` reports an unsatisfied requirement as a failed
   `requirements` check, and the check exits with status `1` (see extension IPC §2.8).
6. **Development builds.** A core without a release version cannot compare versions. A requirement
   naming `weave` then produces one warning on stderr for the invocation and is treated as satisfied
   (see extension IPC §2.9).

## Deferred: Installation

Refusing an incompatible installation, and a future `weave extensions install <name>` subcommand, are
proposals and are not decided here. The proposed rules are in
[Extension Subprocess IPC §2.10](../../specs/extension-ipc.md): stage, check, refuse with an explicit
error, and leave an existing executable unchanged. The open questions for discussion are:

- whether `weave extensions install` is added at all, and when;
- whether the check is mandatory for all installers or advisory for third-party installers;
- whether a refused install should be recoverable with an explicit override, and who may use it.

This ADR will be extended or superseded once those questions are answered.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Warn only, as in the earlier draft | Rejected by the owner: a warning is easy to miss and the command still produces results from a mismatched extension |
| Refuse only when a requirement names `weave` | Rejected: companion-extension requirements have the same failure mode |
| Show requirement status in `extensions list` | Rejected by the owner: status requires running every discovered executable on list, including bundle-local ones in `.weave/bin`, which would be a trust change |
| Enforce at installation now | Deferred: no install step exists yet, so there is nothing to enforce |

## Consequences

- Installations that run an extension with an unmet requirement today will see that command fail after
  the upgrade. The failure is explicit and names the unmet entries, so the fix is to upgrade the core or
  the companion extension.
- `weave extensions list` stays cheap and does not run extensions. Trust is unchanged for listing.
- The new code `EXTENSION_REQUIREMENT_UNMET` joins the error catalog. It is an additive error code in
  `weave.cli/v1`.
- The change breaks installations that run an extension with an unmet requirement. ROADMAP §9 allows
  breaking changes in the v1 contract before 1.0, so no new contract version is needed. Release notes
  must state the change.

## Amendment (2026-11-19): Descriptor-role minimum

The original decision enforces only the `requires` entries an extension declares. That leaves a gap:
an extension released before descriptors, such as `weave-git` v0.9.0 or `weave-code` v0.8.0, declares
no `version` and therefore no requirement core can compare. Core cannot refuse it even though the
generic descriptor contract in [Extension Output Boundary §11](../../specs/extension-output-boundary.md)
requires the 0.11.0 line.

Core now declares the minimum itself for the two roles whose output depends on that contract. A source
provider or project analyzer must declare `version` at or above `0.11.0`. A missing or lower version is
refused with `EXTENSION_REQUIREMENT_UNMET`, exit `1`, with no fallback to a legacy provider or
analyzer. Other roles keep the original rule: an absent `version` is allowed unless a `requires` entry
names that extension. A development build cannot compare versions and warns once, as it does for a
`weave` requirement.

This amendment adds no install-time behavior; the installation rules remain deferred.

## Related Documents

- [Extension Subprocess IPC](../../specs/extension-ipc.md), §2.1, §2.9 and §2.10
- [ADR 0013: Role descriptor registry](0013-role-descriptor-registry.md)
- [ADR 0002: Config paths and additive machine output](0002-config-paths-and-db-location.md)
