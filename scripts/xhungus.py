#!/usr/bin/env python3
"""
Xhungus CLI
Twitter/X to Obsidian converter for the Second-Brian knowledge system.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from archive_parser import TwitterArchiveParser, TweetNormalizer
from note_generator import InboxNoteGenerator, ProcessedNoteGenerator
from state_manager import StateManager, ImportBatch


class XhungusCLI:
    """Main CLI controller for Xhungus."""

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize CLI with optional configuration.

        Config keys:
            - inbox_dir: Where to place inbox notes (default: inbox/tweets)
            - processed_dir: Where to place processed notes (default: notes/tweets)
            - state_file: Path to state file (default: state/import_state.json)
        """
        config = config or {}
        self.inbox_dir = config.get('inbox_dir', 'inbox/tweets')
        self.processed_dir = config.get('processed_dir', 'notes/tweets')
        self.state_file = config.get('state_file', 'state/import_state.json')

        self.state_manager = StateManager(self.state_file)
        self.inbox_generator = InboxNoteGenerator(self.inbox_dir)
        self.processed_generator = ProcessedNoteGenerator(self.processed_dir)

    def import_archive(self, archive_path: str, skip_processed: bool = True):
        """
        Import tweets from a Twitter/X archive ZIP file.

        Args:
            archive_path: Path to the ZIP archive
            skip_processed: Whether to skip already-processed tweets (default: True)
        """
        print(f"Importing archive: {archive_path}")

        # Parse archive
        try:
            parser = TwitterArchiveParser(archive_path)
            raw_tweets = parser.extract_tweets()
            account_info = parser.get_account_info()
        except Exception as e:
            print(f"Error parsing archive: {e}")
            return 1

        # Get author handle
        author_handle = "unknown"
        if account_info and 'username' in account_info:
            author_handle = account_info['username']
            print(f"Archive author: @{author_handle}")
        else:
            print("Warning: Could not determine author handle from archive")

        print(f"Found {len(raw_tweets)} tweets in archive")

        # Filter already-processed tweets
        if skip_processed:
            original_count = len(raw_tweets)
            raw_tweets = [
                t for t in raw_tweets
                if not self.state_manager.is_processed(
                    t.get('tweet', t).get('id_str') or t.get('tweet', t).get('id')
                )
            ]
            skipped = original_count - len(raw_tweets)
            if skipped > 0:
                print(f"Skipping {skipped} already-processed tweets")

        if not raw_tweets:
            print("No new tweets to process")
            return 0

        print(f"Processing {len(raw_tweets)} tweets...")

        # Process tweets with batch context
        processed_count = 0
        error_count = 0

        with ImportBatch(self.state_manager) as batch:
            for i, raw_tweet in enumerate(raw_tweets, 1):
                try:
                    # Normalize
                    normalized = TweetNormalizer.normalize(raw_tweet, author_handle)

                    # Generate inbox note
                    inbox_path = self.inbox_generator.generate_note(normalized)

                    # Generate processed note
                    processed_path = self.processed_generator.generate_note(
                        normalized,
                        inbox_path.name
                    )

                    # Record in state
                    batch.record_tweet(
                        normalized['tweet_id'],
                        normalized['created_at'],
                        str(inbox_path),
                        str(processed_path)
                    )

                    processed_count += 1

                    # Progress indicator
                    if i % 100 == 0:
                        print(f"  Processed {i}/{len(raw_tweets)} tweets...")

                except Exception as e:
                    error_count += 1
                    tweet_id = raw_tweet.get('tweet', {}).get('id_str', 'unknown')
                    print(f"  Error processing tweet {tweet_id}: {e}")
                    continue

        # Summary
        print(f"\n{'='*60}")
        print(f"Import complete!")
        print(f"  Successfully processed: {processed_count}")
        print(f"  Errors: {error_count}")
        print(f"  Inbox notes: {self.inbox_dir}")
        print(f"  Processed notes: {self.processed_dir}")
        print(f"{'='*60}\n")

        # Show stats
        stats = self.state_manager.get_stats()
        print(f"Total tweets in system: {stats['total_processed']}")
        print(f"Latest tweet: {stats['last_created_at']}")

        return 0

    def show_stats(self):
        """Display import statistics."""
        stats = self.state_manager.get_stats()
        print("\nXhungus Import Statistics")
        print("=" * 60)
        print(f"Total processed tweets: {stats['total_processed']}")
        print(f"Latest tweet timestamp: {stats['last_created_at']}")
        print(f"State file: {stats['state_file']}")
        print(f"Last updated: {stats['last_updated']}")
        print("=" * 60)
        return 0


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Xhungus - Twitter/X to Obsidian converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  import-archive <path>   Import tweets from ZIP archive
  stats                   Show import statistics

Examples:
  python xhungus.py import-archive ~/Downloads/twitter-archive.zip
  python xhungus.py stats
        """
    )

    parser.add_argument('command', help='Command to run')
    parser.add_argument('args', nargs='*', help='Command arguments')

    parser.add_argument(
        '--inbox-dir',
        default='inbox/tweets',
        help='Directory for inbox notes (default: inbox/tweets)'
    )
    parser.add_argument(
        '--processed-dir',
        default='notes/tweets',
        help='Directory for processed notes (default: notes/tweets)'
    )
    parser.add_argument(
        '--state-file',
        default='state/import_state.json',
        help='Path to state file (default: state/import_state.json)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-processing of already processed tweets'
    )

    args = parser.parse_args()

    # Build config
    config = {
        'inbox_dir': args.inbox_dir,
        'processed_dir': args.processed_dir,
        'state_file': args.state_file
    }

    cli = XhungusCLI(config)

    # Route commands
    if args.command == 'import-archive':
        if not args.args:
            print("Error: import-archive requires a path argument")
            print("Usage: xhungus.py import-archive <path-to-archive.zip>")
            return 1

        archive_path = args.args[0]
        return cli.import_archive(archive_path, skip_processed=not args.force)

    elif args.command == 'stats':
        return cli.show_stats()

    else:
        print(f"Unknown command: {args.command}")
        print("Run with --help for usage information")
        return 1


if __name__ == '__main__':
    sys.exit(main())
