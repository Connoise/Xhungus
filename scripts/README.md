# Xhungus Scripts

Python implementation of the Xhungus Twitter-to-Obsidian pipeline.

## Requirements

- Python 3.8 or higher
- No external dependencies (uses Python standard library only)

## Modules

### `archive_parser.py`
- `TwitterArchiveParser`: Extracts tweets from ZIP archives
- `TweetNormalizer`: Converts Twitter format to Xhungus internal schema

### `note_generator.py`
- `InboxNoteGenerator`: Creates immutable inbox capture notes
- `ProcessedNoteGenerator`: Creates interpretive processed notes

### `state_manager.py`
- `StateManager`: Tracks import state for idempotent operations
- `ImportBatch`: Context manager for batch imports with automatic state saving

### `xhungus.py`
Main CLI entry point. Implements commands from `../docs/CLI-COMMAND-SPEC.md`.

## Usage

### Import a Twitter Archive

```bash
python xhungus.py import-archive /path/to/twitter-archive.zip
```

This will:
1. Extract and normalize tweets from the archive
2. Generate inbox notes in `inbox/tweets/`
3. Generate processed notes in `notes/tweets/`
4. Track state in `state/import_state.json`

### Custom Output Directories

```bash
python xhungus.py import-archive archive.zip \
  --inbox-dir /path/to/vault/inbox/tweets \
  --processed-dir /path/to/vault/notes/tweets \
  --state-file /path/to/vault/state/xhungus.json
```

### Force Re-import

```bash
python xhungus.py import-archive archive.zip --force
```

Processes all tweets even if already imported (inbox notes are still protected from regeneration).

### View Statistics

```bash
python xhungus.py stats
```

Shows import statistics including total processed tweets and timestamps.

## File Naming Conventions

### Inbox Notes
Format: `YYYYMMDD-HHMMSS-{tweet_id}.md`

Example: `20240115-123045-1234567890.md`

### Processed Notes
Format: `YYYY-MM-DD-Tweet-{short_id}.md`

Example: `2024-01-15-Tweet-34567890.md`

## State Management

The state file (`state/import_state.json`) tracks:
- Processed tweet IDs (for deduplication)
- Last processed timestamp (for incremental imports)
- Content hashes (for change detection)
- Note paths (for reference)

State is automatically saved after each batch import, even if errors occur.

## Idempotency

- Inbox notes are **never regenerated** if they already exist
- Processed notes **can be regenerated** safely
- State tracking ensures duplicate prevention
- Re-running import on same archive is safe

## Error Handling

- Individual tweet errors don't stop the batch
- State is saved even if import fails partway through
- Progress indicators show current status
- Error summary provided at completion
