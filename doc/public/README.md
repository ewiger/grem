# Public documentation (reserved)

`doc/public/` is the reserved home for **published** documentation — the
outward-facing view generated *from* the knowledge base: a rendered API
reference, a handbook, or a book-format site (for example an `mkdocs` or Sphinx
build).

It is **optional**. Most projects never need it, and grem does not stamp it by
default — it only reserves the path so published output has one predictable home
instead of scattering. This project keeps the folder as a placeholder; remove it
if you will never publish.

## Ownership

- **Source of truth** stays in `doc/models/`, `doc/wiki/`, and `doc/proposals/`.
  Treat everything under `doc/public/` as **generated output** — safe to delete
  and rebuild.
- **Building and publishing belong to the project's own tooling** (mkdocs,
  Sphinx, a static-site step in CI). grem never lints, builds, or publishes
  documentation — that boundary is intentional.

See the [knowledge-model](../wiki/knowledge-model.hmd) card for how this category
relates to the rest of `doc/`.
