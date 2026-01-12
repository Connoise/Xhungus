# Xhungus – Twitter to Obsidian

**Xhungus** is a local, run-on-demand system for converting Twitter/X data (ZIP archives or API fetches) into **Obsidian notes** that conform strictly to the **Second-Brian knowledge system**.

Tweets are treated as **time-bound events**, captured immutably, and optionally processed into interpretive notes that emphasize linking over categorization.

This project is intentionally conservative, deterministic, and LLM-constrained.

---

## Core Philosophy

Xhungus follows the principles defined in *Second-Brian*:

- **Capture is immutable**
- **Processing is additive**
- **Interpretation is explicit and reversible**
- **Hubs are places, not conclusions**
- **LLMs assist but do not decide**

Tweets are never rewritten. Later understanding is layered on top, not substituted.

---

## What Xhungus Does

- Parses a Twitter/X **ZIP archive** for full historical backfill
- Optionally fetches **new tweets via the X API** for incremental updates
- Creates:
  - Immutable **inbox capture notes**
  - Safe, additive **processed notes**
- Links tweet media without duplicating large archives
- Tracks state to allow **idempotent re-runs**
- Allows **Claude Code** to enrich notes *within strict constraints*

---

## What Xhungus Does NOT Do

- ❌ No real-time ingestion
- ❌ No automatic hub creation or promotion
- ❌ No forced categorization or ontology enforcement
- ❌ No rewriting of historical captures
- ❌ No “AI decides meaning” behavior

---

## Repository Structure

```text
xhungus-twitter-to-obsidian/
│
├─ docs/                         # Authoritative specs (do not violate)
│   ├─ SYSTEM-OVERVIEW.md
│   ├─ TWEET-NORMALIZATION-SCHEMA.md
│   ├─ INBOX-TWEET-CAPTURE-TEMPLATE.md
│   ├─ PROCESSED-TWEET-NOTE-TEMPLATE.md
│   ├─ TAGGING-GUIDELINES.md
│   ├─ MEDIA-HANDLING-SPEC.md
│   ├─ HUB-INTEGRATION-RULES.md
│   ├─ INCREMENTAL-IMPORT-STATE.md
│   ├─ CLI-COMMAND-SPEC.md
│   └─ CLAUDE-CODE-ROLE-CONSTRAINTS.md
│
├─ scripts/                      # Implementation (language-agnostic)
│
├─ state/                        # Import state, indexes, hashes
│
├─ README.md                     # You are here
└─ .gitignore
