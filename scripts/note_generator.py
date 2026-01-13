"""
Xhungus Note Generator
Creates Obsidian markdown notes from normalized tweet data.
"""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class InboxNoteGenerator:
    """Generates immutable inbox capture notes for tweets."""

    def __init__(self, output_dir: str = "inbox/tweets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_note(self, normalized_tweet: Dict) -> Path:
        """
        Generate an inbox note from a normalized tweet.
        Follows INBOX-TWEET-CAPTURE-TEMPLATE.md

        Returns the path to the created note.
        """
        # Generate filename: YYYYMMDD-HHMMSS-{tweet_id}.md
        created_at = datetime.fromisoformat(normalized_tweet['created_at'])
        timestamp = created_at.strftime('%Y%m%d-%H%M%S')
        tweet_id = normalized_tweet['tweet_id']
        filename = f"{timestamp}-{tweet_id}.md"
        filepath = self.output_dir / filename

        # Don't regenerate if exists (inbox captures are immutable)
        if filepath.exists():
            return filepath

        # Build frontmatter
        frontmatter = self._build_frontmatter(normalized_tweet)

        # Build content
        content = self._build_content(normalized_tweet)

        # Combine
        note_content = f"{frontmatter}\n{content}"

        # Write file
        filepath.write_text(note_content, encoding='utf-8')

        return filepath

    def _build_frontmatter(self, tweet: Dict) -> str:
        """Build YAML frontmatter for inbox note."""
        lines = ["---"]
        lines.append("project: Xhungus – Twitter to Obsidian")
        lines.append("source: twitter")
        lines.append("capture_mode: tweet")
        lines.append(f"captured_at: {tweet['created_at']}")
        lines.append(f"tweet_id: {tweet['tweet_id']}")
        lines.append(f"url: {tweet['url']}")
        lines.append(f"author: {tweet['author_handle']}")

        # Optional fields
        if 'conversation_id' in tweet:
            lines.append(f"conversation_id: {tweet['conversation_id']}")

        if 'in_reply_to_tweet_id' in tweet:
            lines.append(f"in_reply_to: {tweet['in_reply_to_tweet_id']}")

        lines.append("---")
        return "\n".join(lines)

    def _build_content(self, tweet: Dict) -> str:
        """Build the main content body of the inbox note."""
        lines = []

        # Tweet text under "Thought:" heading
        lines.append("\nThought:")
        lines.append(tweet['text'])

        # Media embeds if present
        if 'media_ids' in tweet and tweet['media_ids']:
            lines.append("\n")
            for media_id in tweet['media_ids']:
                # Note: actual media files would need to be symlinked/copied
                # For now, just note their presence
                lines.append(f"[Media: {media_id}]")

        return "\n".join(lines)


class ProcessedNoteGenerator:
    """Generates processed notes for interpretation and linking."""

    def __init__(self, output_dir: str = "notes/tweets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_note(self, normalized_tweet: Dict, inbox_filename: str) -> Path:
        """
        Generate a processed note that references the inbox capture.
        Follows PROCESSED-TWEET-NOTE-TEMPLATE.md

        Returns the path to the created note.
        """
        # Generate filename: YYYY-MM-DD-Tweet-{short_id}.md
        created_at = datetime.fromisoformat(normalized_tweet['created_at'])
        date_str = created_at.strftime('%Y-%m-%d')
        tweet_id = normalized_tweet['tweet_id']
        short_id = tweet_id[-8:]  # Last 8 chars for brevity
        filename = f"{date_str}-Tweet-{short_id}.md"
        filepath = self.output_dir / filename

        # Build note content
        content = self._build_processed_note(normalized_tweet, inbox_filename)

        # Write file
        filepath.write_text(content, encoding='utf-8')

        return filepath

    def _build_processed_note(self, tweet: Dict, inbox_filename: str) -> str:
        """Build processed note content."""
        created_at = datetime.fromisoformat(tweet['created_at'])
        tweet_date = created_at.strftime('%Y-%m-%d')

        lines = [
            f"# {tweet_date} — Tweet",
            "",
            "## Raw Capture",
            f"![[{inbox_filename}]]",
            "",
            "## Context",
            "(What was happening around this tweet, if known)",
            "",
            "## Initial Interpretation",
            "(What this tweet appears to express or explore)",
            "",
            "## Themes",
            "- ",
            "",
            "## Related Hub Notes (Suggested)",
            "- [[Hub - ]]",
            "",
            "## Metadata",
            "- Project: Xhungus – Twitter to Obsidian",
            f"- Source: {tweet['source']}",
            f"- Original Timestamp: {tweet['created_at']}",
            ""
        ]

        return "\n".join(lines)


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """
    Sanitize text for use in filenames.
    Remove or replace characters that are problematic for filesystems.
    """
    # Replace problematic characters
    replacements = {
        '/': '-',
        '\\': '-',
        ':': '-',
        '*': '',
        '?': '',
        '"': '',
        '<': '',
        '>': '',
        '|': '',
        '\n': ' ',
        '\r': ' ',
    }

    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)

    # Collapse multiple spaces
    result = ' '.join(result.split())

    # Truncate if too long
    if len(result) > max_length:
        result = result[:max_length].rstrip()

    return result


if __name__ == '__main__':
    # Basic test
    test_tweet = {
        'tweet_id': '1234567890',
        'created_at': '2024-01-15T12:30:00+00:00',
        'text': 'This is a test tweet',
        'url': 'https://twitter.com/testuser/status/1234567890',
        'author_handle': 'testuser',
        'source': 'twitter-archive'
    }

    inbox_gen = InboxNoteGenerator("test_output/inbox/tweets")
    inbox_path = inbox_gen.generate_note(test_tweet)
    print(f"Created inbox note: {inbox_path}")

    processed_gen = ProcessedNoteGenerator("test_output/notes/tweets")
    processed_path = processed_gen.generate_note(test_tweet, inbox_path.name)
    print(f"Created processed note: {processed_path}")
