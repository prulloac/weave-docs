# AGENTS.md

`weave-docs` owns the project's internal documentation: roadmap, backlog, specifications,
architecture, architecture decisions, knowledge and documentation style. End-user documentation and
BDD behavior scenarios stay in the sibling `weave` repository.

## Scope

- Put specs, ADRs, architecture notes, roadmap, backlog, knowledge and docs style here.
- Keep user-facing docs (`README.md`, guides) and BDD scenarios in `weave`.
- Do not duplicate content; link to the owning repository.
- Link from specs to BDD scenarios in `weave` with absolute GitHub URLs.

## Layout

```text
README.md               this index
ROADMAP.md              delivery status, scope and Feature Register
backlog.md              pipeline state for tracked work
STYLE.md                documentation structure and cross-reference rules
release-checklist.md    release state
specs/                  behavioral contracts, one per feature
architecture/           current design and boundaries
architecture/adr/       immutable decisions
knowledge/              vision and concepts
scripts/check-links.py  local link checker
```

## Commands

- Markdown lint: `npx --yes markdownlint-cli2 "**/*.md"`
- Link check: `python3 scripts/check-links.py`
- Both: `python3 scripts/check-links.py && npx --yes markdownlint-cli2 "**/*.md"`

This repository has no Go build or test target; the product and its tests live in `weave`.

## Conventions

- Read `STYLE.md` before adding or moving docs.
- Specs are contracts: get explicit user approval before the corresponding BDD/TDD work starts in
  `weave`.
- Specs use frontmatter `type: specification` and `status: draft|stable|deprecated`.
- ADRs use `type: Architecture Decision Record`, contiguous `NNNN-kebab-title.md` names, and an
  `ADR NNNN` title and heading.
- Status belongs in frontmatter; delivery status belongs in `ROADMAP.md` and `backlog.md`.
- Every spec appears in `specs/README.md`; every ADR in `architecture/adr/README.md`; every document
  is reachable from `README.md`.
- Use relative links inside this repository. Use `https://github.com/prulloac/weave/blob/main/...`
  for `weave` documents and code, and `https://github.com/prulloac/weave-docs/blob/main/...` only
  when linking from `weave` back here.
- Update `ROADMAP.md` and `backlog.md` together when a phase changes.
- Never mark backlog rows `done`; that is the owner's action.
