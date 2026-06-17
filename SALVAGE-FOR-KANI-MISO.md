# Xhungus → Kani-miso: X/Twitter Import Hand-off

> **Status: Xhungus is retired.** It was a standalone prototype of the
> X/Twitter-archive → Obsidian importer that **Kani-miso** already owns as one
> of its capture surfaces (https://github.com/Connoise/Kani-miso). Maintaining
> a second, diverging implementation is not worthwhile.
>
> This document distills everything from Xhungus worth carrying into
> Kani-miso's X importer: the owner's confirmed design intent (June 2026),
> the tweet normalization schema and note templates, and the **verified
> failure modes** the prototype exhibited. The original, fuller source remains
> frozen in this repo's `docs/` and `scripts/`.

---

## 0. How to use this document

1. For each requirement below, **confirm whether Kani-miso's X importer + specs
   already cover it**, then port only the gaps. Several items are likely
   already handled — this is a checklist, not a mandate.
2. Items marked **✓ verified** are bugs that were *reproduced* in the Xhungus
   prototype. Treat them as ready-made acceptance criteria / regression tests
   for Kani-miso's importer.
3. Items marked **[OPEN]** could not be resolved inside Xhungus (usually
   because they depend on Kani-miso conventions Xhungus never had).

---

## 1. Owner intent (authoritative — from the 20-question review, June 2026)

This is the most valuable salvage: the up-to-date intent for how X import should
behave. Numbers reference the original review questions.

- **Determinism boundary** — Scripts do archiving and organization
  deterministically; the LLM (Kani-miso) is used *only* for synthesis, summary,
  and non-objective classification/organization, and for hub creation. The
  importer itself never calls an LLM. (#5, #14)
- **Immutability** — Notes are not edited after creation. Re-imported tweets are
  **skipped**, even if a later model/analysis change would produce different
  output. Idempotent, write-once. (#6, #12)
- **Note typing** — Notes must be distinguishable by tweet type, and a new
  **"tweet" note type** should exist, distinct from the existing **"thought"
  note type**. **[OPEN]** — the precise boundary depends on Kani-miso's note
  taxonomy. Xhungus had no definition (its `CLAUDE-CODE-ROLE-CONSTRAINTS.md` was
  an empty file). Resolve against Kani-miso's specs. (#7)
- **Threads** — Reconstruct a thread into a **single note** when the reply chain
  resolves cleanly; otherwise fall back to individual notes. Never error out
  over thread reconstruction. (#8)
- **Text fidelity** — Preserve the main tweet body **verbatim**. Expand `t.co`
  links to their `expanded_url` (Twitter-shortened links carry no context and
  hurt preservation). (#9)
- **Media** — Reference each tweet's images/video by **copying** archive media
  (from `data/tweets_media/` in the archive) into an attachments folder *inside
  the vault*, then embedding via Obsidian `![[media/tweets/<file>]]`. **Copy,
  not symlink**, for Windows compatibility; Obsidian only reliably renders
  embeds for files inside the vault. (#10, #17)
- **Timestamps** — Never drop a tweet over a bad date. If `created_at` is
  missing or unparseable, **derive the timestamp from the Snowflake tweet ID**
  (deterministic). Last resort: keep the tweet with a quarantine flag in
  frontmatter. (#11)
- **State / dedup** — "State" = the record of which tweets have already been
  imported. The **vault is the source of truth**: derive already-imported IDs
  by scanning existing note frontmatter rather than relying on a separate,
  losable state file. (#16)
- **Scale** — ~30k tweets total; 100s–1000s new per run. Dedup must be **O(1)
  (set-based)**, and the parser **must handle multi-part archives**. (#15)
- **Secrets** — Any X API credentials go in a gitignored `.env` (already set up
  in this repo's `.gitignore`). Exact creds/usage TBD; API ingestion is not yet
  needed. (#18)
- **Portability** — Linux primary; Windows 11 should also work. (#17)
- **Distribution / docs** — Tool should be shareable; "just run the script" is
  enough (no packaging required). Docs should be thorough enough to be read
  directly or summarized by an LLM after a long gap. (#1, #19, #20)

---

## 2. Tweet normalization schema (portable)

All ingestion paths (archive or API) should emit one internal schema.

**Required:** `tweet_id` (string), `created_at` (ISO-8601), `text` (verbatim),
`url`, `author_handle`, `source` (`twitter-archive` | `x-api`).

**Optional:** `conversation_id`, `in_reply_to_tweet_id`, `referenced_tweets`
(`reply` | `retweet` | `quote` — **see provenance note in §3**), `hashtags[]`,
`mentions[]`, `urls[]` (expanded), `media_ids[]`, `language`.

**Integrity rules:** text never rewritten; normalization idempotent; missing
data preferred over inferred data.

**Snowflake timestamp derivation** (for the #11 fallback):
`created_ms = (int(tweet_id) >> 22) + 1288834974657` (Twitter epoch
2010-11-04). Convert to UTC ISO-8601.

---

## 3. Note model, templates, and provenance

- **Inbox capture (immutable)** and **processed note** templates are preserved
  verbatim in `docs/INBOX-TWEET-CAPTURE-TEMPLATE.md` and
  `docs/PROCESSED-TWEET-NOTE-TEMPLATE.md`. Map these onto Kani-miso's own note
  format rather than introducing a parallel one.
- **Provenance (important).** The prototype wrote every tweet under a
  `Thought:` heading as if it were the author's own words. Retweets, quotes, and
  replies are **not** the author's original thought and must carry attribution
  (this is also why a distinct "tweet" vs "thought" note type was requested in
  #7). Populate `referenced_tweets` and surface the original author for
  RT/quote/reply.

---

## 4. Media / tagging / hub specs (distilled)

- **Media** — Avoid duplicating large archives; preserve traceability to tweet
  IDs; deterministic paths; embed only in the interpretive/processed note;
  missing media is noted, not inferred. (Owner refinement in §1: copy into a
  vault attachments dir; embed with wikilinks.)
- **Tagging** — Tags are optional and descriptive, not structural. Allowed
  classes: `domain/*`, `emotion/*`, `source/twitter`, `note-type/capture`,
  `note-type/processed`. Don't tag for organization alone; don't retrofit tags
  based on later understanding.
- **Hubs** — Hubs are places, not conclusions. The importer **may suggest** hub
  links and **may emit a "missing hubs" report** (pure data), but **must not
  create or promote hubs** — per #14, hub creation/linking is Kani-miso's (LLM)
  job. Full detail in `docs/HUB-INTEGRATION-RULES.md`.

---

## 5. Verified failure modes from the prototype (acceptance criteria)

These were reproduced. Use them as tests for Kani-miso's X importer.

- **✓ Multi-part archives silently truncate.** Real archives split tweets across
  `tweets.js` + `tweets-part1.js` + `tweets-part2.js`…; the prototype read only
  the first matching file → it parsed **1 of 3** tweets with no error. *Fix:*
  read and concatenate **all** `tweets*.js` part files.
- **✓ Dedup type mismatch causes re-imports.** When `id_str` was absent, the
  prototype compared an `int` id against stored `str` ids → `is_processed`
  returned False → duplicate import. *Fix:* always stringify IDs; dedup via a
  set.
- **✓ Regeneration destroys interpretation.** Re-running note generation
  rewrote the processed note wholesale, **silently erasing human-added
  interpretation**. This directly contradicted the "additive / immutable"
  philosophy. *Fix:* write-once; never regenerate; vault as source of truth
  (§1).
- **✓ Non-deterministic date fallback.** Missing dates fell back to
  `datetime.now()`, which fed the filename — breaking determinism and
  idempotency. *Fix:* Snowflake derivation (§2).
- **Other smells to avoid:** no RT/quote provenance; `t.co` links left
  unexpanded; non-atomic state writes (no temp-file + rename); unsanitized
  `tweet_id` flowed into filesystem paths; dead code (`content_hashes`
  subsystem and `sanitize_filename` were never wired up); CLI returned exit 0
  even when individual tweets failed.

---

## 6. "Confirm Kani-miso already covers" checklist

- [ ] Multi-part archive parsing (`tweets*.js`)
- [ ] Tweet-type taxonomy ("tweet" vs "thought") + RT/quote/reply provenance
- [ ] Thread → single-note reconstruction (graceful fallback)
- [ ] Media copy-into-vault + Obsidian embed (copy, not symlink)
- [ ] Snowflake-ID timestamp fallback; never drop a tweet
- [ ] Verbatim text + `t.co` expansion
- [ ] Vault-as-source-of-truth dedup, O(1), at ~30k scale
- [ ] Atomic write→commit (Kani-miso's README lists this for Phase 2 — likely ✓)
- [ ] `.env` for any future X API credentials

---

## 7. Frozen source (for reference)

- `docs/*.md` — the original operational specs. Note:
  `docs/CLAUDE-CODE-ROLE-CONSTRAINTS.md` was an **empty file**; the AI-role
  rules it should have held are instead covered by Kani-miso's `CLAUDE.md` and
  `specs/05-ai-and-ops.md`.
- `scripts/*.py` — the prototype implementation (parser, normalizer, note
  generators, state manager, CLI). Functional for small archives; see §5 for
  why it should not be extended.
