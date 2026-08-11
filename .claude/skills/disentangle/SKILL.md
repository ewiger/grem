---
name: disentangle
description: Remove archaeology from a document — replace internal pointers (§5.3, F21, "see above", "invariant 6", "as discussed") with the claim they stand for, and address anything that remains by coordinate (file > section > subsection > "quote") instead of by number. Use when the user complains about cross-references, paragraph or section numbers, dense hypertext, or having to dig through layers to read something; when they say a document is sedimentary, tangled, or unreadable without opening five other files; or when they ask to disentangle, flatten, or de-reference a text. Not a summarizer and not a style rewrite — it changes how the text refers, not what it says.
---

# disentangle

A document should be readable start to finish, once, by someone who has opened nothing else.

Sedimentary writing is the opposite: built from buried layers of history, each sentence resting on
a pointer to an earlier one, so reading it means excavating it. Every `§5.3` and `see invariant 6`
is a hole in the page the reader has to fill by going somewhere else. A page of those is not a
dense document, it is a **thin document plus homework**.

Disentangling means doing that digging yourself, once, at write time — so no reader has to do it
again, ever.

```
disentangle(text) = resolve every internal pointer into the claim it stands for,
                    and address what remains by coordinate, not by number
```

## The two rules

### 1. You do the digging, not the reader

Every internal pointer names a claim the reader cannot see. Go read it. Write down what it says.
Put that in the text.

```
BAD:   This is P1 applied to queries, and it is why §1 and §4 are
       stated before F21 lands.

GOOD:  Queries are subject to the same rule as writes: they never
       observe a partial commit. That is why the isolation guarantee
       and the read-path contract are both fixed before the query
       planner is written.
```

The bad version costs four lookups across three files and communicates nothing standing alone. The
good version costs the writer ten minutes, once.

**An identifier may follow a claim so a reader can find the row. It may never be the claim.**

```
GOOD:  A `full` snapshot writes every record (`R8`).
BAD:   R8 is why this matters.
```

### 2. Address by coordinate, never by number

When a pointer genuinely has to survive, the coordinate system is:

```
file > section header > subheader > "quoted text"
```

Names, not numbers. Down to a quote when the target is a specific sentence.

```
BAD:   see §9 step 6
BAD:   as described in section 4.2, paragraph 3
BAD:   per requirement 35

GOOD:  see design.md > Recovery > "restore nothing, answer 500"
GOOD:  see design.md > Shape of the archive > The record
GOOD:  the design says a rotation boundary "is written as kind: full"
```

Why names beat numbers:

- **A number is not a claim.** `§9` tells the reader nothing about what is there. `Jump > "restore
  nothing"` already communicates most of the point without the trip.
- **Numbers rot on the next edit.** Insert a section and every citation to it is silently wrong.
  Nothing errors, nothing warns, and the reader lands somewhere plausible and false. A named
  heading survives having its neighbours renumbered.
- **A quote is checkable.** A reader can grep for it. If it is not found, the reference is stale
  and the reader knows immediately, rather than reading the wrong paragraph with confidence.

Which follows: **do not number headings.** Numbered headings are what makes `§5.3` citable in the
first place. Remove the numbers and the bad habit has nothing to attach to.

## Scarcity of links

**See also** links and footnotes are permitted at the **bare minimum** and no more.

- One **See also** section, at the end. Not scattered inline.
- A footnote only when the material is genuinely optional — a reader who skips it must lose
  nothing load-bearing.
- If a claim matters, it goes in the text. A footnote is not a place to park an important
  condition.

The test: delete every link and footnote. If the document still says everything it needs to say,
they were correctly scoped. If it now has holes, those holes were the defect — inline them.

## Normalization

A cross-reference is a join. `see §5.3` says: the value you need is stored somewhere else, go
fetch it. Reading a sedimentary document means running those joins by hand, and a human is a very
slow query engine.

So note which direction this skill runs. Normalizing a schema factors repeated data out into its
own table behind a key — which is the right shape for storage and exactly the wrong shape for a
reader, because it pays for correctness with joins on every read. Inlining a pointer into the
claim it stands for is **de**normalization: copy the value into the row so the read is a single
fetch. And it buys the classic denormalization problem along with the classic win — the copy can
drift from its source. Three constraints keep the graph in hand.

**One home per claim.** Every claim is *defined* in exactly one document. Copies elsewhere are
restatements sized to local need, not second definitions: a copy may say less, never something
different. When a copy and its home disagree, the home is right and the copy is the bug. If you
cannot name the home of a claim, that is the defect to fix before any rewriting.

**A link budget.** Count the outbound coordinates a document needs before it can be understood at
all. One or two is a document with context. Five is a document stored in the wrong place —
renaming its pointers will not save it. Merge the material, or promote one document to the hub the
others point at. Links that merely help a reader go deeper are not charged against the budget;
links that are load-bearing for the current page are.

**Depth one.** Flatten transitive pointers. `A` → `B` → `C` puts the reader two joins deep, and
the second join is invisible from `A` — nothing on the page warns that the trip has another leg.
Resolve chains at write time so no reader chases more than one hop. A shallow star (a hub and its
leaves) is readable at any size; a chain of four is not readable at all.

The read path and the reference path can differ, and should. The definition exists once, for
correctness. The inline copy exists wherever it is needed, for reading.

## What must not change

This is a transformation of **reference**, not of **content**. The logic is untouched:

- what implies what, what causes what
- conditions, exceptions, alternatives, dependencies
- `must` vs `should` vs `may`; `all` vs `some` vs `only` vs `never`
- observed vs inferred vs proposed vs hypothetical
- current state vs intended state

Two failure modes to watch for, both of which quietly change meaning:

**Dropping a pointer instead of inlining it.** Deleting `see §7` without importing what §7 said
removes a claim. That is a semantic loss and is forbidden. Inline it or keep it.

**Importing the target's argument along with its claim.** Pull in the constraint the pointer stands
for. Do not pull in the target's supporting reasoning, examples, or caveats — that adds assertions
the source never made.

## Keep the names of things

Identifiers that name a **thing in the system** stay exactly as written, in code formatting:
`flush_pending_writes`, `archive.idx`, `MAX_RETRIES = 5`, `POST /v1/archives/restore`, `409`,
`--recieve-buffer`, 4 MiB, `2^20`.

Never paraphrase one into a description. `POST /v1/archives/restore` does not become "the restore
endpoint". Never correct a spelling that looks wrong — `--recieve-buffer` keeps its transposed
vowels, because that is what the user has to type. Never refer to one thing two different ways;
repeating the exact term is what tells a reader it is the same thing.

This does not contradict rule 1. The difference is what the identifier refers to:

| Identifier names | Example | Do |
|---|---|---|
| a location in a document | `§5.3`, `F21`, `Q7`, "invariant 6" | replace it with the claim |
| a thing in the system | `archive.idx`, `409`, `segment_size` | keep it verbatim |

Replace pointers to claims. Keep names of things.

## Procedure

1. **Inventory the pointers.** List every internal cross-reference: section numbers, item numbers,
   feature or question IDs, "see above", "as discussed", "the previous section", links to sibling
   documents.
2. **Read every target.** Note the claim each one stands for. Mark any you could not open.
3. **Inline them.** Replace each pointer with its claim. Where a pointer must survive, rewrite it
   as a coordinate.
4. **Unnumber the headings**, and convert inbound citations to names.
5. **Cut the links** to the minimum that survives the deletion test above.
6. **Check the shape.** How many documents must a reader open to understand this one, and how deep
   does any chain go? Flatten anything past one hop. If the count is still high, say so — the fix
   is where the material lives, not how it is worded.
7. **Check nothing was lost:** every claim still present, same modality, same conditions, same
   scope, nothing added.

**If you cannot read a target, leave the pointer as written.** Guessing what it says is
fabrication, which is a worse defect than the archaeology it was meant to fix. Say which ones you
left alone and why.

## Renaming headings breaks inbound citations

Removing numbers from headings silently invalidates any `§5.3` citation from **other** files. Grep
for inbound references before renaming, fix the ones you own, and say plainly which ones you
changed. Never do it silently to a file that others cite.

## When not to use it

- **Trackers, status tables, indexes, changelogs.** Their rows are ID lookups by design and are
  read one at a time, not as prose. `STATUS.md` is supposed to be a table of IDs.
- **Specs with externally-defined numbering.** RFC section numbers, legal clauses, standards
  references, and API error codes are addresses in someone else's document. They are names of
  things, not pointers into your text.
- **Text that is already flat.** Rewriting it churns wording for nothing.
- **Anything already published or agreed** — commit messages, released docs, quoted material.
  Rewriting these changes a record.
