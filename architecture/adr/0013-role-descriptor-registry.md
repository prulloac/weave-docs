---
type: Architecture Decision Record
title: "ADR 0013: Role Descriptor Registry for Extension Roles"
description: "Describes each extension role once, so discovery, invocation, validation and limits are shared, and adding a role does not require edits across packages. Wire formats do not change."
tags:
  - "architecture"
  - "extensions"
  - "registry"
  - "ipc"
status: accepted
---

# ADR 0013: Role Descriptor Registry for Extension Roles

## Context

Core invokes extensions for several roles: enrichment, project analysis, reranking, scoring, embeddings,
source providers, extension data, codecs and crypto providers. [Extension Subprocess IPC](../../specs/extension-ipc.md)
defines the shared runner, and [ADR 0012](0012-extension-owned-documents-and-opaque-options.md) moved
extension output to generic data.

Each role still has its own request and response types, its own invocation path in
`engine/extensions`, its own flags in the CLI, and its own validation and limits. Changing one role or
adding one means coordinated edits across several packages, and the same discovery, timeout, size
and stderr rules are repeated for each role. The duplication is the main cost of the extension
boundary, and it grows with every role.

## Decision

1. **One descriptor per role.** Each role is described once in `engine/extensions`. A descriptor
   names the manifest role key, the transport (a JSON protocol identifier, `weave.cli/v1` or
   `weave.source/v1`, or raw bytes for codec extensions named `weave-codec-<name>`), the request and
   response types, the default timeout, the response and request size bounds, the failure policy
   (fallback to core results, failure of the operation, or refusal before invocation for unsatisfied
   requirements, as ADR 0014 requires) and the CLI flag that selects it.
2. **One invocation path.** Core dispatches every role through the same routine. The routine performs
   discovery, `--describe --json` validation, requirement evaluation (ADR 0014), the timeout, size caps,
   stderr capture and response
   validation. Role code supplies only typed request construction and response validation.
3. **Static registration.** Descriptors are compiled into core. Core does not load roles at runtime.
   Extensions remain subprocesses, as ADR 0012 requires.
4. **No wire change.** Manifests, envelopes, CLI flags and exit codes are unchanged. The behavior-
   preservation gate in ADR 0012 applies: the existing conformance and BDD suites for every role must
   pass without changes to their expectations.
5. **New roles still follow the pipeline.** A role needs its own specification and behavior scenarios
   before it is registered, as the SDD → BDD → TDD rules require. The descriptor does not replace them.

## Alternatives Considered

| Alternative | Decision |
| --- | --- |
| Keep per-role invocation functions | Rejected: duplication grows with each role and each limit change must be repeated |
| Generate role code from the contract schema | Rejected for now: the schemas do not describe timeouts, failure policy or flags, so generation would still need hand-written descriptors |
| In-process plugin interface for roles | Rejected: ADR 0012 keeps subprocess isolation and language independence |
| Runtime role loading from manifests | Rejected: a manifest could then add a role core does not know how to validate |

## Consequences

- Adding a role means adding one descriptor and its typed request and response validation; discovery,
  timeouts and limits are inherited.
- Limits and failure policy become visible in one table, which makes review of changes to them easier.
- The refactor carries regression risk. It is gated by the existing suites and must land in small
  steps, one role at a time, with the same observable output for each step.
- The descriptor table becomes a review hotspot. Changes to it need the same review as any contract
  change.
- Batching and parallel invocation ([extension IPC](../../specs/extension-ipc.md)) are easier to add
  once invocation is shared. Their own decisions remain separate.

## Related Documents

- [Extension Subprocess IPC specification](../../specs/extension-ipc.md)
- [ADR 0003: Extension protocol ownership](0003-extension-protocol-ownership-and-weave-ai-extraction.md)
- [ADR 0012: Extension-owned synthetic documents and opaque provider options](0012-extension-owned-documents-and-opaque-options.md)
- [Privacy and extension architecture](../privacy-and-extensions.md)
