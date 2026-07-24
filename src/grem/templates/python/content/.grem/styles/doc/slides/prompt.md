# Turn a prose doc into a numbered D2 "visual story"

Apply this documentation style to the source document named in the prompt
header. Read that document in full first.

**Goal:** Take the long-form Markdown doc — one that explains a system's design
or lifecycle — and produce a companion folder of small, numbered diagrams (using
D2) that retell it as a sequence of slides: one idea per diagram, read top to
bottom like a deck.

## Philosophy

- **One idea per diagram, not one diagram per doc.** Never cram a whole system
  into a single canvas. Split the source doc's sections into the smallest visual
  units that each carry one idea, zoomed to the altitude that idea needs (a
  single stage, a single before/after comparison, one worked example).
- **The diagram folder is a compact companion, not a replacement.** The README
  that binds the diagrams together reads as the short version; the original prose
  doc remains the long version. Every diagram set links back to its source doc,
  and the source doc links forward to the diagram set — discoverable from both
  directions.
- **Source vs. generated output is a hard split.** The `.d2` files (and the
  README's narrative) are the only hand-edited sources. The rendered
  `.svg`/`.png` are build artifacts — but they are still committed, so the
  diagrams render in plain Markdown viewers (GitHub, IDE preview) without anyone
  needing the D2 toolchain installed. Any diff that touches a `.d2` file but not
  its rendered twin is a sign a build step was skipped.

## File and folder conventions

- One subfolder per source doc, named after it.
- Files inside: `NN-short-slug.d2` — a numeric prefix fixes reading order in a
  plain directory listing (`01-vision.d2`, `02-mechanism.d2`, …). Insert a new
  idea in the middle by renumbering the tail, not by using decimals or letters.
- A single-idea diagram that is naturally two beats (e.g. "problem, then
  solution") may be split into `NN-slug_1.d2` / `NN-slug_2.d2` rather than forced
  into one crowded canvas.
- A thin `build.sh` per folder that just delegates to one shared build script —
  so every folder is independently buildable, but there is exactly one real
  rendering implementation to maintain.
- A `README.md` per folder that alternates narrative and image: a short
  paragraph (a tightened excerpt or summary of the matching section in the
  source doc), then the diagram image, repeated per diagram in numbered order.
  Close with a "Related documentation" section linking back to the source doc and
  any doc the diagrams reference by name.

## D2 authoring conventions

- Each `.d2` file defines its own local classes (e.g. a `block` class for
  shape/color reuse) rather than importing a shared palette — D2 has no
  cross-file import in this style, and each diagram should be readable
  standalone.
- Establish a consistent but per-diagram color semantics, e.g.: one color for
  "in the group / allowed" actors, another for "excluded / denied" actors or
  failure paths, a distinct fill for role/group nodes (often drawn as a cylinder
  shape), a neutral grey for schema/data objects (often a "page" shape), a green
  stroke for "granted" edges, a dashed red stroke for "denied" edges.
- Bookend most diagrams with a `title:` text node (`near: top-center`, bold,
  larger font) and a short explanatory `note:` text node (`near: bottom-center`,
  smaller font) — so each diagram is self-explanatory even lifted out of
  context.
- Group related nodes into named containers (e.g. "Lane A", "Users", "Groups",
  "Schema Objects") when a diagram has categorically distinct clusters of
  elements — this reads better than a flat node soup and mirrors how the prose
  doc names those categories.

## Decomposition method (how to break prose into slides)

- Read the source doc's own section headers — they are usually already the right
  granularity for "one diagram per idea" (a Vision section, a Stage, a
  comparison, a worked example, a summary).
- For each section, ask: what is the single relationship or transition this
  section is arguing for? Draw only that — the actors, the objects they act on,
  and the edges that represent the mechanism (grants, ownership, membership, data
  flow).
- Sequence the diagrams so the whole set has a narrative arc: usually
  vision/motivation → underlying mechanism → stages of the lifecycle in order → a
  worked example with concrete names → a summary diagram that recaps the whole
  arc in one compressed view.
- When a stage in the story naturally has multiple lanes or actors happening
  concurrently (e.g. two systems evolving independently, or upstream setup vs.
  downstream consumption), give each lane its own diagram rather than merging
  them — unless the comparison between lanes is itself the point of that slide.

## Regeneration workflow

- `d2` compiles `.d2` → `.svg`. `rsvg-convert` (librsvg) rasterizes `.svg` →
  `.png` — preferred over D2's own PNG export, because that requires a headless
  browser dependency, while rasterizing the SVG only needs a small, reliable
  library that can also decode D2's embedded fonts.
- Provide a Docker fallback (`terrastruct/d2:latest`) for environments without
  local tooling, and document the fallback command explicitly, since this is
  often the first thing to break in a new environment.
- Rule of thumb to enforce in review: a `.d2` change without its regenerated
  `.svg`/`.png` twin in the same change is incomplete.
