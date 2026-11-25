---
type: specification
title: "Extension Authoring Guide Specification"
description: "Defines the content a third-party author needs to build a weave-<name> extension without reading the Weave source."
tags:
  - "specification"
  - "extensions"
  - "documentation"
status: stable
---

# Specification: Extension Authoring Guide

## 1. Overview

Extensions are the main way to add behavior to Weave, but the protocol is spread across several
specifications. This specification defines what the authoring guide must contain, so a developer can
write a working extension from one document. The guide itself is end-user documentation and lives in
[`weave/docs/guides`](https://github.com/prulloac/weave/blob/main/docs/guides); this specification owns
its required content, and links to the owning specifications instead of restating them.

Non-goals:

- Scaffolding commands. `weave extensions new` is a separate proposal.
- The codec protocol. It is covered by [Codec Extensions](codec-extensions.md).
- Installation. Installing extensions is an open proposal in
  [Extension Subprocess IPC §2.10](extension-ipc.md).

## 2. Required content

The guide must contain these sections, in this order:

1. **What an extension is.** `weave-<name>` executables, discovery in `.weave/bin` and on `PATH`, and the
   bundle-local trust gate with `weave extensions trust`.
2. **Manifest.** The `--describe --json` fields `v`, `name`, `version`, `requires`, `protocols`,
   `roles`, `cache_key` and `capabilities`, with a minimal valid example. Links to extension IPC §2.1
   and §2.9.
3. **Transport.** One request per process, JSON on stdin and stdout only, diagnostics on stderr, exit `0`
   on success and `1` on failure, the default timeout and size bounds, and the opt-in `batch` envelope.
   Links to extension IPC §2.2.
4. **Roles.** One short subsection per role, linking the owning section: enrichment, reranking, scoring,
   embeddings, project analysis, source provider and tokenizer. Codecs link to their own
   specification.
5. **Requirements.** How to declare `requires`, what a refusal looks like (`EXTENSION_REQUIREMENT_UNMET`),
   and what a development build does.
6. **Conformance.** How to run `weave extensions check <name>` and read its result, including the
   codec form and the `requirements` failure.
7. **Worked example.** A complete POSIX shell enrichment extension that passes the canonical request in
   the golden corpus.
8. **Testing.** Using the golden corpus as fixtures, and the rule that extensions must never open the
   index database or write into the bundle.
9. **Release.** Tag format `vX.Y.Z`, the rule that the manifest `version` matches the release tag, and
   the naming rule that keeps the binary discoverable.

## 3. Rules the guide must state

- Extensions never receive index paths or write access through the protocol.
- Core performs no network call on an extension's behalf; any network use is the extension's own opt-in.
- Extensions must not execute the bundle's code or build tools.
- Examples must not contain secrets.

## 4. Acceptance Criteria

1. A developer who has not read the Weave source can write an enrichment extension that passes the
   canonical enrichment request and response from the golden corpus.
2. Every envelope shape in the guide matches the golden corpus.
3. The guide links rather than copies the protocol specifications.

## Related Documents

- [Extension Subprocess IPC](extension-ipc.md)
- [Codec Extensions](codec-extensions.md)
- [Privacy & Extensions](../architecture/privacy-and-extensions.md)
