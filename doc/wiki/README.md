# Wiki

`doc/wiki/` is the project's knowledge base: a graph of cross-linked
**hyper-markdown** (`.hmd`) cards, one concept per file. Each card defines a
single thing and links to its neighbours with `[[wikilinks]]`, so understanding
emerges from small, connected cards rather than one long document.

Start from any card and follow the links. See
[hyper-markdown.hmd](hyper-markdown.hmd) for the format itself; grouped sets live
in topic subfolders (for example [models/](models/)). The
[knowledge-model.hmd](knowledge-model.hmd) card indexes how `doc/wiki/` relates
to the other `doc/` categories.

## Writing a card

The authoring convention — naming, structure, and register — is the `doc/hmd`
documentation style, not repeated here:
[.grem/styles/doc/hmd/prompt.md](../../.grem/styles/doc/hmd/prompt.md). Render it
against a source document with `grem new --type doc --style hmd <source>` and an
agent applies it.
