# Weave Project Documentation

This repository owns the project's internal documentation: roadmap, backlog, specifications,
architecture, architecture decisions, knowledge and documentation style. End-user documentation and
BDD behavior scenarios stay in the sibling [`weave`](https://github.com/prulloac/weave) repository.

## Start here

- [Roadmap](ROADMAP.md) — delivery status, scope and the Feature Register.
- [Backlog](backlog.md) — pipeline state for tracked work.
- [Specifications](specs/README.md) — one behavioral contract per feature.
- [Architecture](architecture/index.md) — current layers, topology and boundaries.
- [Architecture decisions](architecture/adr/README.md) — accepted, proposed and superseded ADRs.
- [Knowledge](knowledge/index.md) — vision and concepts.
- [Documentation style](STYLE.md) — structure, status and cross-reference rules.
- [Release checklist](release-checklist.md) — release state.

## Repository split

| Content | Repository |
| --- | --- |
| Install, quickstart, commands, configuration, OKF usage | [`weave/README.md`](https://github.com/prulloac/weave/blob/main/README.md) |
| BDD behavior scenarios and Go test mapping | [`weave/docs/bdd`](https://github.com/prulloac/weave/blob/main/docs/bdd/README.md) |
| Roadmap, backlog, specs, architecture, ADRs, knowledge, style | this repository |

Specs link to their BDD scenarios in `weave` with absolute GitHub URLs. The `weave` repository keeps
end-user documentation, BDD scenarios and repository instructions.

## Issues

This repository does not accept issues. Report first-party defects and documentation errors in
[`prulloac/weave`](https://github.com/prulloac/weave/issues/new/choose); security reports use private
vulnerability reporting there. The triage policy is in
[1.0 Stability Gate and Issue Policy](specs/stability-gate.md).

## Contributing

- Read [AGENTS.md](AGENTS.md) before changing docs.
- Run `python3 scripts/check-links.py` and `npx --yes markdownlint-cli2 "**/*.md"`.
- The link check also enforces that every document is reachable from this README.
- Keep links relative inside this repository; use absolute GitHub URLs for `weave`.
