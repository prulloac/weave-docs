# Documentation Style Guide

Weave documentation is part of the release contract. A reader should be able to tell what is
shipped, what is deferred and which document owns each fact without opening more than two pages.

This repository owns project documentation. End-user documentation and BDD behavior scenarios stay
in the sibling [`weave`](https://github.com/prulloac/weave) repository.

## Document classes

| Class | Location | Owns | Does not own |
| --- | --- | --- | --- |
| Task guide | `weave/README.md`, `weave/docs/guides/**` | Install, quickstart, commands and examples | Delivery status or internal design |
| Roadmap | `ROADMAP.md` | Feature delivery status and release scope | Behavioral contracts |
| Backlog | `backlog.md` | Pipeline phase and tracked work | Delivery status |
| Specification | `specs/**` | Behavioral contract | Delivery status or phase history |
| Behavior scenario | `weave/docs/bdd/**` | Observable behavior examples | Algorithms or implementation |
| Architecture | `architecture/**` | Current design and boundaries | Roadmap promises |
| ADR | `architecture/adr/**` | Immutable decisions | Current task instructions |
| Knowledge | `knowledge/**` | Vision and concepts | Status or contract |

## Status

- Specs use `draft`, `stable` or `deprecated` in frontmatter.
- ADRs use `proposed`, `accepted`, `superseded` or `rejected` in frontmatter.
- Do not add a `Status:` line to the body. Delivery state belongs to the roadmap and backlog.
- Write shipped behavior in the present tense. Put future work in the roadmap and backlog, not in a
  reference page.
- A document's status describes the document, not the feature. A shipped feature can have a `draft`
  spec while the contract is being reviewed, but that is an exception to close before release.

## Decision Records

- ADR decision text is immutable. Correcting a fact, a broken link or a typo that changes no meaning
  uses a dated `## Errata (YYYY-MM-DD)` section at the end of the ADR.
- Extending an accepted decision without reversing it uses a dated
  `## Amendment (YYYY-MM-DD): <topic>` section at the end. The original text stays as written.
- Reversing a decision needs a new ADR. The old ADR's frontmatter changes to `superseded` and links
  the replacement; it is never rewritten to read as if it always said so.
- Errata and amendments do not change the ADR number or title.

## Numbering

- ADR files are `NNNN-kebab-title.md`, contiguous from `0001`. The number in the filename, title,
  index and references must match.
- Feature Register IDs are contiguous from `1` and sorted ascending.
- Every `Phase`, `Wave` and milestone ID referenced by another document must exist.
- Anchors are checked; do not link to a heading that no longer exists.

## Cross-references

- Link the owner instead of restating a fact.
- Every Feature Register row links one authoritative spec and one backlog tier.
- Every spec appears in [`specs/README.md`](specs/README.md).
- Every behavior set appears in
  [`weave/docs/bdd/README.md`](https://github.com/prulloac/weave/blob/main/docs/bdd/README.md) and
  names its executable tests or checks.
- Every ADR appears in [`architecture/adr/README.md`](architecture/adr/README.md).
- Every document is reachable from [`README.md`](README.md).

## Versions

- The current `weave` release is stated once, in the status line at the top of
  [`ROADMAP.md`](ROADMAP.md). Other documents link to the roadmap instead of restating it.
- Released versions are git tags in the owning repository. Each member has its own tag line.
- Wave labels such as `0.7` or `0.8` in the roadmap and backlog name delivery waves. They are not
  product versions.
- `python3 scripts/check-consistency.py` fails when the status line disagrees with the latest `weave`
  tag, when a register row or backlog row links a missing spec, or when a spec is not indexed.

## Voice and structure

- Open with one sentence that states the document's purpose.
- Name the audience when it is not obvious.
- Use short paragraphs, tables and runnable examples.
- Use one vocabulary: bundle, document, concept, source, database, in-memory.
- Do not describe retired commands, frameworks or product surfaces. Keep a short non-goals note only
  when the history prevents a real misunderstanding.
- Prefer concrete commands and outputs over internal phase history.
- Do not use unexplained IDs. Link the definition.

## Links and examples

- Use relative Markdown links for documents in this repository.
- Use absolute GitHub URLs for `weave` documents and code:
  `https://github.com/prulloac/weave/blob/main/...`.
- Link to headings only when the heading is stable; prefer linking the document.
- Keep examples copy-pasteable and free of placeholder secrets.
- Run the link/reachability check (`python3 scripts/check-links.py`) and
  `npx --yes markdownlint-cli2 "**/*.md"` before opening a documentation pull request.
