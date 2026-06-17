# Xhungus — Retired

> ⚠️ **This project is retired and superseded by [Kani-miso](https://github.com/Connoise/Kani-miso).**
>
> Xhungus was a standalone prototype that converted a Twitter/X archive into
> Obsidian notes. That capability now lives — more maturely and integrated with
> other capture surfaces (Telegram, articles, PDFs, images), a SQLite queue,
> authoritative specs, and a test suite — inside **Kani-miso**, where the
> X/Twitter archive is one of several ingestion sources. Maintaining a second,
> diverging implementation here is not worthwhile.

## What to read instead

- **[`SALVAGE-FOR-KANI-MISO.md`](SALVAGE-FOR-KANI-MISO.md)** — the hand-off
  document. It distills everything from this repo worth carrying into
  Kani-miso's X importer: the owner's confirmed design intent (June 2026), the
  tweet normalization schema and note templates, and the verified failure modes
  the prototype exhibited (so they aren't repeated).
- **[Kani-miso](https://github.com/Connoise/Kani-miso)** — the active engine.

## What this repo was

A local, run-on-demand Python CLI (standard library only) that:

- parsed a Twitter/X archive ZIP and normalized tweets to an internal schema,
- generated immutable "inbox" capture notes and interpretive "processed" notes,
- tracked import state in a JSON file for idempotent re-runs.

It worked for small archives but had real gaps for the intended use case
(notably: it read only the first `tweets*.js` part file, so large archives were
silently truncated; re-generation could overwrite human interpretation; and
dates/dedup were fragile). See `SALVAGE-FOR-KANI-MISO.md` §5 for the full,
reproduced list — these are now acceptance criteria for Kani-miso's importer.

## Status of this repository

Frozen for historical reference. The original specs are in `docs/` and the
prototype implementation is in `scripts/`. No further development will happen
here; please use Kani-miso.
