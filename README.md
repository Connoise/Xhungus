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
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A Twitter/X archive ZIP file (download from your Twitter settings)
- An Obsidian vault (or directory where notes will be stored)

### Quick Start

1. **Download your Twitter archive**
   - Go to Twitter/X Settings → Your Account → Download an archive of your data
   - Wait for the email with your download link
   - Extract and keep the ZIP file

2. **Run the import**
   ```bash
   cd scripts
   python xhungus.py import-archive /path/to/twitter-archive.zip
   ```

3. **Find your notes**
   - Inbox captures: `inbox/tweets/`
   - Processed notes: `notes/tweets/`
   - Import state: `state/import_state.json`

### Import to Your Obsidian Vault

Point the output directories to your vault:

```bash
python xhungus.py import-archive archive.zip \
  --inbox-dir /path/to/vault/inbox/tweets \
  --processed-dir /path/to/vault/notes/tweets \
  --state-file /path/to/vault/.xhungus-state.json
```

### View Statistics

```bash
python xhungus.py stats
```

---

## Implementation Status

| Feature | Status |
|---------|--------|
| Archive parsing | ✅ Complete |
| Tweet normalization | ✅ Complete |
| Inbox note generation | ✅ Complete |
| Processed note generation | ✅ Complete |
| State tracking | ✅ Complete |
| CLI (import-archive) | ✅ Complete |
| CLI (stats) | ✅ Complete |
| X API incremental updates | 🚧 Planned |
| LLM enrichment | 🚧 Planned |
| Media handling | 🚧 Planned |
| Missing hubs report | 🚧 Planned |

---

## Project Documentation

All specifications are in the `docs/` directory. These are authoritative and must not be violated by implementation:

- **[SYSTEM-OVERVIEW.md](docs/SYSTEM-OVERVIEW.md)** - Core architecture and principles
- **[TWEET-NORMALIZATION-SCHEMA.md](docs/TWEET-NORMALIZATION-SCHEMA.md)** - Internal data format
- **[INBOX-TWEET-CAPTURE-TEMPLATE.md](docs/INBOX-TWEET-CAPTURE-TEMPLATE.md)** - Immutable capture template
- **[PROCESSED-TWEET-NOTE-TEMPLATE.md](docs/PROCESSED-TWEET-NOTE-TEMPLATE.md)** - Interpretation note template
- **[CLI-COMMAND-SPEC.md](docs/CLI-COMMAND-SPEC.md)** - Command interface
- **[HUB-INTEGRATION-RULES.md](docs/HUB-INTEGRATION-RULES.md)** - Hub linking guidelines
- **[INCREMENTAL-IMPORT-STATE.md](docs/INCREMENTAL-IMPORT-STATE.md)** - State tracking spec

See `scripts/README.md` for detailed implementation documentation.

---

## Design Constraints

- **No external dependencies** - Uses Python standard library only
- **Idempotent by design** - Safe to re-run on the same archive
- **Inbox immutability** - Capture notes are never regenerated or modified
- **Deterministic output** - Same input always produces same result
- **Local only** - No network calls except for optional API updates
- **Conservative defaults** - LLM assistance requires explicit invocation
