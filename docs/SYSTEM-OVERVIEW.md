# Xhungus – Twitter to Obsidian: System Overview

## Purpose
Xhungus converts Twitter/X data (archive or API) into Obsidian notes that comply with the Second-Brian knowledge system.

Tweets are treated as **time-bound events** and therefore qualify as individual captures.

## Design Principles
- Deterministic first, LLM-assisted second
- Raw captures are immutable
- Processing adds interpretation without rewriting history
- Hubs are suggested, never auto-promoted
- Scripts run locally and only when invoked

## Data Sources
- Twitter/X ZIP archive (primary backfill)
- Twitter/X API (optional incremental updates)

## Output Targets
- /inbox/tweets/  (raw captures)
- /notes/tweets/  (processed notes)
- /media/tweets/  (symlinked or copied media)

## Non-Goals
- No real-time ingestion
- No forced categorization
- No automatic hub creation
