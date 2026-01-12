# Xhungus Import State Tracking

The importer maintains a persistent state file.

## Stored Values
- processed_tweet_ids
- last_created_at
- content_hashes
- note_paths

## Rules
- Inbox captures are never regenerated
- Processed notes may be appended safely
- State file is authoritative for deduplication
