# Xhungus Quick Start Guide

## What You Just Built

A fully functional Twitter-to-Obsidian pipeline that:
- ✅ Parses Twitter/X archive ZIP files
- ✅ Normalizes tweets to a strict internal schema
- ✅ Generates immutable inbox capture notes
- ✅ Creates interpretive processed notes ready for enrichment
- ✅ Tracks state for idempotent re-runs
- ✅ Provides a CLI for easy operation

## Try It Now

### 1. Test with Sample Data

```bash
cd scripts
python test_example.py
```

This creates sample tweets and processes them into `test_output/`.

### 2. Use with Real Twitter Archive

Download your Twitter archive from your account settings, then:

```bash
cd scripts
python xhungus.py import-archive /path/to/twitter-archive.zip
```

### 3. Import to Your Obsidian Vault

```bash
python xhungus.py import-archive archive.zip \
  --inbox-dir /path/to/vault/inbox/tweets \
  --processed-dir /path/to/vault/notes/tweets
```

## File Structure Created

```
scripts/
├── archive_parser.py      # ZIP extraction + normalization
├── note_generator.py      # Markdown note creation
├── state_manager.py       # Deduplication tracking
├── xhungus.py            # Main CLI entry point
├── test_example.py       # Test/demo script
├── README.md             # Implementation docs
└── requirements.txt      # (No external deps needed!)
```

## Example Output

### Inbox Note (Immutable Capture)
```markdown
---
project: Xhungus – Twitter to Obsidian
source: twitter
capture_mode: tweet
captured_at: 2024-01-15T12:30:00+00:00
tweet_id: 1234567890
url: https://twitter.com/testuser/status/1234567890
author: testuser
---

Thought:
This is my first sample tweet! Testing the Xhungus parser.
```

### Processed Note (Ready for Interpretation)
```markdown
# 2024-01-15 — Tweet

## Raw Capture
![[20240115-123000-1234567890.md]]

## Context
(What was happening around this tweet, if known)

## Initial Interpretation
(What this tweet appears to express or explore)

## Themes
-

## Related Hub Notes (Suggested)
- [[Hub - ]]

## Metadata
- Project: Xhungus – Twitter to Obsidian
- Source: twitter-archive
- Original Timestamp: 2024-01-15T12:30:00+00:00
```

## What's Next?

The archive parser is complete. Next steps for development:

1. **X API Integration** - Incremental updates via Twitter API
2. **LLM Enrichment** - Claude-assisted interpretation (following CLAUDE-CODE-ROLE-CONSTRAINTS.md)
3. **Media Handling** - Symlink/copy images and videos
4. **Hub Reports** - Generate missing hub reports

See docs/CLI-COMMAND-SPEC.md for planned commands:
- `update-api` - Fetch new tweets since last import
- `enrich-notes` - AI-assisted interpretation
- `report-missing-hubs` - Find referenced but non-existent hubs

## Design Principles in Action

✅ **Capture is immutable** - Inbox notes never regenerated once created
✅ **Processing is additive** - Processed notes can be safely regenerated
✅ **Deterministic** - Same input = same output, always
✅ **Idempotent** - Safe to re-run on same archive
✅ **Conservative** - No auto-decisions, human approval required
✅ **Spec-compliant** - All docs/ specifications followed exactly
