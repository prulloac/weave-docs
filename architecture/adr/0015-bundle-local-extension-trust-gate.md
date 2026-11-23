---
type: Architecture Decision Record
title: "ADR 0015: Bundle-Local Extension Trust Gate"
description: "Refuses to run bundle-local weave-<name> executables until the user trusts their exact path and hash, so cloning a bundle cannot execute its code by accident."
tags:
  - "architecture"
  - "extensions"
  - "security"
  - "trust"
status: accepted
---

# ADR 0015: Bundle-Local Extension Trust Gate

## Context

Weave discovers `weave-<name>` executables in `<bundle>/.weave/bin/` before looking on `PATH`, and
[Extension Subprocess IPC §2.1](../../specs/extension-ipc.md) treats running them as deliberate. That
is convenient for a bundle the user authored, but it makes cloning or unpacking an untrusted bundle a
code-execution vector: the first `ingest`, `search --rerank`, `audit` or `sync` can run whatever the
bundle ships. [ADR 0012](0012-extension-owned-documents-and-opaque-options.md) keeps extensions as
subprocesses; it does not decide whether a bundle may introduce one.

The owner decided that trust must be explicit, recorded per user, and bound to the exact executable.
A bundle must never be able to trust itself, and `extensions list` must stay a plain directory scan,
so trust state cannot appear there.

## Decision

1. **Trust is per user and hash-pinned.** `~/.weave/trust.yaml` maps an extension name to the absolute
   executable path and the SHA-256 of its bytes. A matching entry is required before a bundle-local
   executable runs. `WEAVE_HOME` and the existing config resolution move the file as they do for the
   index database.
2. **A bundle cannot grant trust.** `.weave/trust.yaml`, manifests, environment variables inside a
   bundle and `PATH` entries have no authority. A bundle file may only narrow what the user trusted;
   the first release implements no bundle file.
3. **Only bundle-local executables are gated.** Extensions installed on `PATH` are already a user
   action and run as today. Codec, crypto, source, enrichment and all other roles share the gate.
4. **Untrusted is skipped, explicit is refused.** An auto-discovered untrusted extension is skipped
   with one warning on stderr (`EXTENSION_UNTRUSTED` text) and core behavior continues. Naming it
   explicitly (`--with-enricher`, `--with-embedder`, `--embedder`, `--rerank`, `--scorer`, `--git`, a
   codec, crypto provider or `extensions check`) fails before invocation with the
   `EXTENSION_UNTRUSTED` code, exit `1`, and a hint naming the trust command.
5. **Trust is managed by command and by file.** `weave extensions trust <name> [<path>]` resolves the
   executable, records path and hash, and prints the hash; `untrust <name>` removes the entry; and
   `trusted [<path>]` lists entries with their path, hash and whether the file still matches.
   Hand-editing `trust.yaml` remains valid. No command prompts interactively, so JSON workflows and
   CI stay non-interactive.
6. **Re-trust on change.** Replacing the executable changes its hash and returns it to untrusted until
   the user trusts it again. A moved bundle changes the path and behaves the same way.
7. **List stays a scan.** `extensions list` does not read `trust.yaml` and reports no trust field.
   `extensions trusted` is the read surface for trust state.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Trust by path only | Rejected: an updated binary would keep running without review |
| Committed `.weave/trust.yaml` that grants trust | Rejected: a cloned bundle could trust its own code |
| Warn but run | Rejected: the owner asked for a block, not a suggestion |
| Refuse every command that discovers an untrusted extension | Rejected: it breaks ordinary ingest and search for a bundle the user is inspecting |
| Signature verification or a registry | Deferred: it needs key distribution and is larger than the local-first trust decision here |

## Consequences

- The first run of a new or updated bundle-local extension requires one explicit trust command.
- CI and automation seed `trust.yaml` or install extensions on `PATH`; nothing depends on a prompt.
- A hash change is visible in `extensions trusted`, so review is possible before re-trusting.
- `extensions check` gains one failure mode and its report gains an `untrusted`-style requirement
  failure; BDD scenarios cover both the skip and the explicit refusal.
- Extension authors must document the trust step; the authoring guide owns the wording.
