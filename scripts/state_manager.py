"""
Xhungus State Manager
Tracks import state for idempotent operations and deduplication.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime


class StateManager:
    """
    Manages import state for Xhungus.

    Follows INCREMENTAL-IMPORT-STATE.md:
    - Stores processed_tweet_ids, last_created_at, content_hashes, note_paths
    - Ensures inbox captures are never regenerated
    - Allows safe appending to processed notes
    - State file is authoritative for deduplication
    """

    def __init__(self, state_file: str = "state/import_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from file, or initialize if not exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load state file: {e}")
                print("Initializing new state.")

        # Default state structure
        return {
            'processed_tweet_ids': [],
            'last_created_at': None,
            'content_hashes': {},
            'note_paths': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }

    def save(self):
        """Persist state to disk."""
        self.state['metadata']['last_updated'] = datetime.now().isoformat()

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def is_processed(self, tweet_id: str) -> bool:
        """Check if a tweet has already been processed."""
        return tweet_id in self.state['processed_tweet_ids']

    def mark_processed(self, tweet_id: str, created_at: str,
                      inbox_path: str, processed_path: Optional[str] = None):
        """
        Mark a tweet as processed.

        Args:
            tweet_id: The tweet ID
            created_at: ISO-8601 timestamp of tweet creation
            inbox_path: Path to the inbox note
            processed_path: Optional path to the processed note
        """
        if tweet_id not in self.state['processed_tweet_ids']:
            self.state['processed_tweet_ids'].append(tweet_id)

        # Update last_created_at if this tweet is newer
        if (self.state['last_created_at'] is None or
                created_at > self.state['last_created_at']):
            self.state['last_created_at'] = created_at

        # Store note paths
        self.state['note_paths'][tweet_id] = {
            'inbox': str(inbox_path),
            'processed': str(processed_path) if processed_path else None
        }

    def compute_content_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def store_content_hash(self, tweet_id: str, content: str):
        """Store content hash for a tweet."""
        content_hash = self.compute_content_hash(content)
        self.state['content_hashes'][tweet_id] = content_hash

    def has_content_changed(self, tweet_id: str, content: str) -> bool:
        """Check if content has changed since last import."""
        if tweet_id not in self.state['content_hashes']:
            return True

        current_hash = self.compute_content_hash(content)
        stored_hash = self.state['content_hashes'][tweet_id]

        return current_hash != stored_hash

    def get_processed_count(self) -> int:
        """Get count of processed tweets."""
        return len(self.state['processed_tweet_ids'])

    def get_last_created_at(self) -> Optional[str]:
        """Get the timestamp of the most recent processed tweet."""
        return self.state['last_created_at']

    def get_note_paths(self, tweet_id: str) -> Optional[Dict[str, str]]:
        """Get inbox and processed note paths for a tweet."""
        return self.state['note_paths'].get(tweet_id)

    def get_all_processed_ids(self) -> List[str]:
        """Get list of all processed tweet IDs."""
        return self.state['processed_tweet_ids'].copy()

    def reset(self):
        """Reset state (use with caution)."""
        self.state = {
            'processed_tweet_ids': [],
            'last_created_at': None,
            'content_hashes': {},
            'note_paths': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }
        self.save()

    def get_stats(self) -> Dict:
        """Get import statistics."""
        return {
            'total_processed': self.get_processed_count(),
            'last_created_at': self.get_last_created_at(),
            'state_file': str(self.state_file),
            'last_updated': self.state['metadata'].get('last_updated'),
            'created_at': self.state['metadata'].get('created_at')
        }


class ImportBatch:
    """
    Context manager for batch imports.
    Ensures state is saved even if import fails partway through.
    """

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.tweet_count = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Save state regardless of success/failure
        self.state_manager.save()
        if exc_type is None:
            print(f"\nBatch import complete: {self.tweet_count} tweets processed")
        else:
            print(f"\nBatch import interrupted: {self.tweet_count} tweets processed before error")
        return False  # Don't suppress exceptions

    def record_tweet(self, tweet_id: str, created_at: str,
                    inbox_path: str, processed_path: Optional[str] = None):
        """Record a processed tweet in this batch."""
        self.state_manager.mark_processed(tweet_id, created_at, inbox_path, processed_path)
        self.tweet_count += 1


if __name__ == '__main__':
    # Basic test
    state = StateManager('test_output/state/test_state.json')

    print("Initial state:")
    print(json.dumps(state.get_stats(), indent=2))

    # Simulate processing tweets
    state.mark_processed('123', '2024-01-01T00:00:00Z', '/inbox/123.md', '/notes/123.md')
    state.mark_processed('456', '2024-01-02T00:00:00Z', '/inbox/456.md', '/notes/456.md')

    state.save()

    print("\nAfter processing:")
    print(json.dumps(state.get_stats(), indent=2))
    print(f"Is 123 processed? {state.is_processed('123')}")
    print(f"Is 789 processed? {state.is_processed('789')}")
