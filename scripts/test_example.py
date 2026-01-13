#!/usr/bin/env python3
"""
Example/Test Script for Xhungus
Demonstrates the archive parser functionality without requiring a real archive.
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime, timedelta

from archive_parser import TwitterArchiveParser, TweetNormalizer
from note_generator import InboxNoteGenerator, ProcessedNoteGenerator
from state_manager import StateManager


def create_sample_archive(output_path: str = "sample_archive.zip"):
    """
    Create a sample Twitter archive ZIP file for testing.
    Mimics the structure of a real Twitter archive.
    """
    # Sample tweets in Twitter archive format
    sample_tweets = [
        {
            "tweet": {
                "id_str": "1234567890",
                "id": 1234567890,
                "created_at": "Mon Jan 15 12:30:00 +0000 2024",
                "full_text": "This is my first sample tweet! Testing the Xhungus parser. #testing",
                "conversation_id_str": "1234567890",
                "lang": "en",
                "entities": {
                    "hashtags": [{"text": "testing"}],
                    "user_mentions": [],
                    "urls": []
                }
            }
        },
        {
            "tweet": {
                "id_str": "1234567891",
                "id": 1234567891,
                "created_at": "Tue Jan 16 14:45:00 +0000 2024",
                "full_text": "Second tweet with a mention @someone and a link https://example.com",
                "conversation_id_str": "1234567891",
                "lang": "en",
                "entities": {
                    "hashtags": [],
                    "user_mentions": [{"screen_name": "someone"}],
                    "urls": [{"url": "https://t.co/xyz", "expanded_url": "https://example.com"}]
                }
            }
        },
        {
            "tweet": {
                "id_str": "1234567892",
                "id": 1234567892,
                "created_at": "Wed Jan 17 09:15:00 +0000 2024",
                "full_text": "A reply tweet testing threading",
                "conversation_id_str": "1234567890",
                "in_reply_to_status_id_str": "1234567890",
                "lang": "en",
                "entities": {
                    "hashtags": [],
                    "user_mentions": [],
                    "urls": []
                }
            }
        }
    ]

    # Sample account info
    sample_account = [
        {
            "account": {
                "username": "testuser",
                "accountId": "123456",
                "createdAt": "2020-01-01T00:00:00.000Z"
            }
        }
    ]

    # Create the ZIP archive
    with zipfile.ZipFile(output_path, 'w') as zf:
        # Write tweets.js (with Twitter's JS prefix format)
        tweets_content = f"window.YTD.tweets.part0 = {json.dumps(sample_tweets, indent=2)}"
        zf.writestr('data/tweets.js', tweets_content)

        # Write account.js
        account_content = f"window.YTD.account.part0 = {json.dumps(sample_account, indent=2)}"
        zf.writestr('data/account.js', account_content)

    print(f"Created sample archive: {output_path}")
    return output_path


def test_parser():
    """Test the archive parser with sample data."""
    print("\n" + "=" * 60)
    print("Testing Xhungus Archive Parser")
    print("=" * 60 + "\n")

    # Create sample archive
    archive_path = create_sample_archive()

    # Parse the archive
    parser = TwitterArchiveParser(archive_path)

    # Extract tweets
    print("Extracting tweets...")
    tweets = parser.extract_tweets()
    print(f"Found {len(tweets)} tweets\n")

    # Get account info
    account = parser.get_account_info()
    if account:
        username = account.get('username', 'unknown')
        print(f"Account: @{username}\n")
    else:
        username = "testuser"

    # Normalize tweets
    print("Normalizing tweets...")
    normalized_tweets = []
    for raw_tweet in tweets:
        normalized = TweetNormalizer.normalize(raw_tweet, username)
        normalized_tweets.append(normalized)
        print(f"  - Tweet {normalized['tweet_id']}: {normalized['text'][:50]}...")

    print("\n" + "=" * 60)
    print("Normalized Tweet Example")
    print("=" * 60)
    print(json.dumps(normalized_tweets[0], indent=2))

    # Generate notes
    print("\n" + "=" * 60)
    print("Generating Notes")
    print("=" * 60 + "\n")

    inbox_gen = InboxNoteGenerator("test_output/inbox/tweets")
    processed_gen = ProcessedNoteGenerator("test_output/notes/tweets")
    state_mgr = StateManager("test_output/state/test_state.json")

    for tweet in normalized_tweets:
        # Check if already processed
        if state_mgr.is_processed(tweet['tweet_id']):
            print(f"Skipping already processed tweet: {tweet['tweet_id']}")
            continue

        # Generate inbox note
        inbox_path = inbox_gen.generate_note(tweet)
        print(f"Created inbox note: {inbox_path}")

        # Generate processed note
        processed_path = processed_gen.generate_note(tweet, inbox_path.name)
        print(f"Created processed note: {processed_path}")

        # Update state
        state_mgr.mark_processed(
            tweet['tweet_id'],
            tweet['created_at'],
            str(inbox_path),
            str(processed_path)
        )

    # Save state
    state_mgr.save()
    print(f"\nState saved: {state_mgr.state_file}")

    # Show stats
    print("\n" + "=" * 60)
    print("Statistics")
    print("=" * 60)
    stats = state_mgr.get_stats()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nCheck the following directories:")
    print("  - test_output/inbox/tweets/")
    print("  - test_output/notes/tweets/")
    print("  - test_output/state/")

    # Show a sample note
    print("\n" + "=" * 60)
    print("Sample Inbox Note")
    print("=" * 60)
    sample_note_path = Path("test_output/inbox/tweets").glob("*.md").__next__()
    print(sample_note_path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    test_parser()
