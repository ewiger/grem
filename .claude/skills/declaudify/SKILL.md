---
name: declaudify
description: Rewrite text to remove Claude's prose style while preserving its logic exactly. Use when the user asks to declaudify, de-slop, or de-AI text; asks for "plain/simple English", "say it plainly", "less AI-sounding", "stop writing like a chatbot"; complains about cross-references, hedging, bolded topic sentences, or em-dash pileups; or asks to rewrite a previous message or a document in a plainer register. Not a summarizer — length may stay the same.
---

# declaudify

```
declaudify(text) = semantic-preserving style transformation
```

Change the expression. Do not change the reasoning.

This is **not summarization** and not "make it shorter." Shorter is desirable only where
redundancy can be removed without changing the logical structure. A correct declaudify can come
out the same length, or longer, if the original packed several claims into one dense clause that
now needs three plain sentences.

## The hard invariant

The rewrite MUST preserve the logic of the source. Treat the source as a technical proposition
that may be restated but must not be semantically altered.

Preserve exactly:

- what implies what
- what causes what
- conditions under which statements hold
- necessary vs. sufficient conditions
- negation
- exceptions
- alternatives
- dependencies
- sequence and temporal relationships
- scope of claims
- quantified claims: `all`, `some`, `only`, `never`, `may`
- uncertainty: `probably`, `appears`, `may`, `possibly`
- normative strength: `must` ≠ `should` ≠ `may`
- factual status: observed ≠ inferred ≠ proposed ≠ hypothetical
- current state vs. intended or future state

Rules that follow from it:

- Do not merge two distinct claims into one if the merge loses a distinction.
- Do not strengthen a claim.
- Do not weaken a claim.
- Do not infer conclusions that are not explicitly present.
- Do not delete a sentence just because it sounds obvious, if it carries a condition,
  qualification, consequence, or exception.

The target:

```
meaning(output) ≈ meaning(input)
style(output)   ≠ Claudish
```

## The failure mode that matters most

Almost every bad declaudify is the same bug: **a hedge or a condition gets read as filler and
dropped, and the claim silently gets stronger.** Watch for it specifically.

```
Input:
  If DATABASE_URL is set, all environments use that database;
  otherwise each environment uses its local default.

BAD:
  All environments use the same database.

GOOD:
  If DATABASE_URL is set, all environments use it.
  Otherwise, each environment uses its local default.
```

```
Input:
  The ALB targets port 5173, so this may expose the Vite development
  server in production.

BAD:
  The ALB exposes the Vite development server in production.

GOOD:
  The ALB targets port 5173, which may expose the Vite development
  server in production.
```

```
Input:
  Appending never rewrites existing rows, so an append should only
  dirty the new pages — assuming the file was not already preallocated
  past the old end.

BAD:
  An append only dirties the new pages.

GOOD:
  Appending never rewrites existing rows. So an append should only
  dirty the new pages, unless the file was already preallocated past
  the old end.
```

In each case the bad version reads better and says something different. Plainness is not worth a
single bit of meaning.

## What "Claudish" is

Remove these. None of them carry logic; all of them can go without touching the invariant above.

**Structure**

- Leading with the mechanism before the reader knows what problem it solves. Order should be:
  problem, why it is tractable, mechanism, consequence.
- Cross-references that force a lookup. See "No archaeology" below — it is the largest single
  class of Claudish structure and has its own rules.
- Section headers on text too short to need navigation.
- A closing paragraph that restates what was just said.
- An unprompted "want me to..." offer at the end of every turn.

**Paragraph**

- A **bolded topic phrase** opening paragraph after paragraph in a row.
- Rule-of-three rhythm: three examples, three adjectives, three parallel clauses, every time.
- "It's not just X, it's Y." "Not merely X but Y."
- Meta-commentary about the writing itself: "worth noting", "two points to pin down", "the key
  insight here".

**Sentence**

- Em-dash chains and stacked appositives that hold four clauses in one breath.
- Front-loaded subordinate clauses that delay the subject.
- Passive voice where an actor exists.
- Nominalization: "perform a calculation of" for "calculate".

**Word**

- Hedging scaffolding with no propositional content: "It's worth noting that", "That said",
  "I should mention", "Importantly".
- Sycophancy: "Great question", "You're absolutely right", "Excellent point".
- Hype adjectives: powerful, elegant, robust, seamless, crucial, comprehensive, significant.
- "delve", "leverage" (verb), "utilize", "facilitate", "underscore", "landscape", "realm".

Note the asymmetry: hedging **scaffolding** goes ("It's worth noting that X" → "X"), but
epistemic hedges **stay** ("X may cause Y" stays "may").

## No archaeology

A text is a complete record, not a web of references. Write it so it can be read start to finish,
once, by someone who has opened no other file. State plainly what the thing is and what its
features are.

Do not thread prose with identifiers standing in for the claim itself: feature IDs (`F21`),
question IDs (`Q7`), section refs (`§5.3`), requirement numbers ("requirement 35"), or links to
sibling documents. Restate the constraint instead of citing where it lives.

**An identifier may follow a claim so a reader can locate the row. It may never be the claim.**

Every surviving pointer goes in one **See also** section at the end, plus footnotes if genuinely
needed.

The failure this prevents:

```
BAD:
  This is P1 applied to queries, and it is why §1 and §4 are stated
  before F21 lands.
```

Four lookups in three files, and it communicates nothing on its own. A page of that is a page of
pointers. Requiring archaeology to parse a sentence is the defect, whether or not each individual
link is correct.

Subsections are titled by **what they cover, not by number**. Numbered headings are what make
`§5.3` citable in the first place, and a named heading survives an edit that renumbers its
neighbours.

**Trackers are exempt.** A `STATUS.md` is a table of IDs by nature — that is its job, and its rows
are read one at a time rather than as prose. The rule binds records and prose documents.

### The one place this collides with semantic invariance

Replacing `§5.3` with what §5.3 says means importing text that is not in the source. That is
**importing, not inferring**, and it is legal — but only under these conditions:

1. **Read the target first.** Open the referenced section, feature row, or file and restate what
   is actually there.
2. **If you cannot read it, leave the pointer alone.** An unresolvable reference stays as written.
   Guessing what it says is fabrication, which is a worse defect than the archaeology.
3. **Import the claim, not the argument.** Pull in the constraint the pointer stands for. Do not
   pull in the target's supporting reasoning, examples, or caveats — that changes what the source
   asserts by adding to it.
4. **Deleting a pointer without inlining it drops a claim.** That is a semantic loss and is
   forbidden. Inline it or keep it.

**Renaming numbered headings has a side effect: it breaks inbound citations from other files.**
If anything outside the text under rewrite cites `§5.3`, renaming that heading silently
invalidates the citation. Say so when you do it; do not do it silently to a file that others cite.

## What to write instead

- Short sentences. One idea per sentence.
- Plain words where a plain word exists.
- Active voice with a named actor.

Plain register applies to the **prose around the technical content**, never to the technical
content itself. Simple English is not simplified content.

## Keep the names

Every name stays exactly as written, in code formatting, unchanged:

- file names and paths — `index.bin`, `src/store/engine.rs`, `config.toml`
- functions, methods, types, fields, variables — `flush_pending_writes`,
  `IndexShard::merge_segment`, `page_size`
- constants and their values — `DEFAULT_PAGE_SIZE = 4096`
- config keys, table names, environment variables — `[cache] max_entries`,
  `APP_DATA_DIR`
- API routes, HTTP methods, status codes — `POST /admin/cache/purge`, `409`
- CLI flags and commands — `--recieve-buffer`, `cargo test`
- error strings and log messages, quoted verbatim
- numbers, units, sizes, versions — 4 MiB, `2^20` entries, format v3
- formulas and code — `H(n) = H(n-1) + delta(n)`
- domain terms of art — WAL, tombstone, compaction, quorum

Rules:

- **Never paraphrase a name into a description.** `flush_pending_writes` does not become "the
  write flush helper". `POST /admin/cache/purge` does not become "the purge endpoint".
- **Never expand, translate, or prettify an identifier** for readability.
- **Never correct an identifier**, even when its spelling or casing looks wrong. It is a literal.
  `--recieve-buffer` keeps its misspelling.
- **Keep code formatting**, so the text stays greppable. A rewrite that renames things into prose
  is a rewrite nobody can search.
- **A gloss may follow a name on first use, only if the source already supplies it.** Do not invent
  one.

**Elegant variation is a bug.** Referring to one thing three different ways to avoid repetition is
a Claudish habit and it is wrong here: in technical text, repeating the exact term is what tells
the reader it is the same thing. Pick the source's name and use it every time.

### Why this does not contradict "no archaeology"

Both rules are about identifiers, and they point opposite ways. The difference is what the
identifier refers to.

- `§5.3`, `F21`, `Q7` name a **location in a document**. The reader cannot see the claim without
  going there, so the pointer must be replaced by the claim.
- `flush_pending_writes`, `index.bin`, `409` name a **thing in the system**. The name *is* the
  thing. Replacing it with a description destroys the reference and makes the text unsearchable.

Replace pointers to claims. Keep names of things.

## Procedure

1. **Extract the claims first.** Before rewriting, list what the source asserts, one line per
   claim, tagging each with its modality (must / should / may / observed / inferred / proposed)
   and its conditions. This list is the contract.
2. **Resolve the pointers.** Collect every identifier and cross-reference in the source. Read each
   target and note the claim it stands for. Mark the ones you could not open — those stay as
   written.
3. **Rewrite** in plain register, inlining the resolved claims.
4. **Check the rewrite against the list.** Every claim present, same modality, same conditions,
   same scope, nothing added.
5. **Check for the silent-strengthening bug** specifically: search the output for claims that lost
   an `if`, `unless`, `may`, `only`, `not`, or `assuming`.
6. **Check that no pointer was deleted without being inlined**, and that no inlined claim brought
   the target's reasoning along with it.
7. **Check the names.** Every identifier in the source appears in the output, spelled and cased
   identically, in code formatting. None was turned into a description, and none is referred to by
   two different names.

For a short passage, do steps 1 and 4 mentally. For a document, do them literally.

## Invocation

- `/declaudify` with no argument — rewrite your own previous message.
- `/declaudify <path>` — rewrite that file in place.
- `/declaudify <quoted text>` — rewrite that text.

Return the rewrite alone. Do not preface it with an explanation of what you changed, and do not
append a summary of the edits. If a source sentence was genuinely ambiguous and the two readings
have different logical content, ask rather than pick.

## When not to use it

- Text that is already plain. Rewriting it churns wording for nothing.
- Trackers, status tables, and indexes. Their rows are ID lookups by design and are read one at a
  time, not as prose.
- Quoted material, spec language, error strings, commit messages already written, and anything
  with a defined external format. Rewriting these changes a record.
- Cases where the user wants it **shorter**. That is summarization, which loses claims by design.
  Confirm which one they want before dropping anything.
