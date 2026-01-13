"""
Xhungus Archive Parser
Extracts and normalizes tweets from Twitter/X ZIP archives.
"""

import json
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class TwitterArchiveParser:
    """Parses Twitter/X archive ZIP files and extracts tweet data."""

    def __init__(self, archive_path: str):
        self.archive_path = Path(archive_path)
        if not self.archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        if not zipfile.is_zipfile(self.archive_path):
            raise ValueError(f"Not a valid ZIP file: {archive_path}")

    def extract_tweets(self) -> List[Dict]:
        """
        Extract tweets from the archive.
        Returns list of raw tweet objects from the archive.
        """
        tweets = []

        with zipfile.ZipFile(self.archive_path, 'r') as archive:
            # Twitter archives can have tweets in different locations
            possible_paths = [
                'data/tweets.js',
                'data/tweet.js',
                'tweets.js',
                'tweet.js'
            ]

            tweet_file = None
            for path in possible_paths:
                try:
                    tweet_file = archive.read(path).decode('utf-8')
                    break
                except KeyError:
                    continue

            if not tweet_file:
                raise ValueError(
                    f"No tweets.js or tweet.js found in archive. "
                    f"Checked paths: {possible_paths}"
                )

            # Twitter archives prefix the JSON with a variable assignment
            # Example: "window.YTD.tweets.part0 = " or "window.YTD.tweet.part0 = "
            # We need to strip this and parse the JSON
            tweets = self._parse_twitter_js_file(tweet_file)

        return tweets

    def _parse_twitter_js_file(self, content: str) -> List[Dict]:
        """
        Parse a Twitter .js file that has the format:
        window.YTD.tweets.part0 = [...]
        """
        # Remove the variable assignment prefix
        # Match patterns like "window.YTD.tweets.part0 = " or similar
        json_match = re.search(r'=\s*(\[.*\])\s*;?\s*$', content, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)
        else:
            # If no prefix found, assume it's already JSON
            json_str = content

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse tweet data as JSON: {e}")

        return data

    def get_account_info(self) -> Optional[Dict]:
        """
        Extract account information from the archive.
        Returns account metadata if available.
        """
        with zipfile.ZipFile(self.archive_path, 'r') as archive:
            possible_paths = [
                'data/account.js',
                'account.js'
            ]

            for path in possible_paths:
                try:
                    account_file = archive.read(path).decode('utf-8')
                    # Parse similar to tweets.js
                    json_match = re.search(r'=\s*(\[.*\])\s*;?\s*$', account_file, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        if data and len(data) > 0:
                            return data[0].get('account', {})
                except (KeyError, json.JSONDecodeError):
                    continue

        return None


class TweetNormalizer:
    """Normalizes Twitter archive format to Xhungus internal schema."""

    @staticmethod
    def normalize(raw_tweet: Dict, author_handle: str) -> Dict:
        """
        Convert raw archive tweet to normalized schema.

        Follows TWEET-NORMALIZATION-SCHEMA.md:
        - Required: tweet_id, created_at, text, url, author_handle, source
        - Optional: conversation_id, in_reply_to_tweet_id, referenced_tweets,
                   hashtags, mentions, urls, media_ids, language
        """
        # Twitter archive wraps tweet data in a 'tweet' key
        tweet_data = raw_tweet.get('tweet', raw_tweet)

        tweet_id = tweet_data.get('id_str') or tweet_data.get('id')
        if not tweet_id:
            raise ValueError("Tweet missing required 'id' field")

        # Parse created_at to ISO-8601
        created_at_str = tweet_data.get('created_at', '')
        created_at = TweetNormalizer._parse_twitter_date(created_at_str)

        # Get full text (handling both 'full_text' and 'text' fields)
        text = tweet_data.get('full_text') or tweet_data.get('text', '')

        # Build tweet URL
        url = f"https://twitter.com/{author_handle}/status/{tweet_id}"

        # Required fields
        normalized = {
            'tweet_id': str(tweet_id),
            'created_at': created_at,
            'text': text,
            'url': url,
            'author_handle': author_handle,
            'source': 'twitter-archive'
        }

        # Optional fields
        if 'conversation_id_str' in tweet_data or 'conversation_id' in tweet_data:
            normalized['conversation_id'] = str(
                tweet_data.get('conversation_id_str') or tweet_data.get('conversation_id')
            )

        if 'in_reply_to_status_id_str' in tweet_data or 'in_reply_to_status_id' in tweet_data:
            normalized['in_reply_to_tweet_id'] = str(
                tweet_data.get('in_reply_to_status_id_str') or
                tweet_data.get('in_reply_to_status_id')
            )

        # Extract entities
        entities = tweet_data.get('entities', {})

        if 'hashtags' in entities and entities['hashtags']:
            normalized['hashtags'] = [h['text'] for h in entities['hashtags']]

        if 'user_mentions' in entities and entities['user_mentions']:
            normalized['mentions'] = [m['screen_name'] for m in entities['user_mentions']]

        if 'urls' in entities and entities['urls']:
            normalized['urls'] = [u['expanded_url'] or u['url'] for u in entities['urls']]

        # Media handling
        if 'media' in entities and entities['media']:
            normalized['media_ids'] = [m['id_str'] for m in entities['media']]

        # Extended entities for additional media
        extended_entities = tweet_data.get('extended_entities', {})
        if 'media' in extended_entities:
            media_ids = normalized.get('media_ids', [])
            for m in extended_entities['media']:
                mid = m['id_str']
                if mid not in media_ids:
                    media_ids.append(mid)
            if media_ids:
                normalized['media_ids'] = media_ids

        if 'lang' in tweet_data:
            normalized['language'] = tweet_data['lang']

        return normalized

    @staticmethod
    def _parse_twitter_date(date_str: str) -> str:
        """
        Convert Twitter date format to ISO-8601.
        Twitter format: "Wed Oct 10 20:19:24 +0000 2018"
        ISO-8601 format: "2018-10-10T20:19:24+00:00"
        """
        if not date_str:
            return datetime.now().isoformat()

        try:
            dt = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
            return dt.isoformat()
        except ValueError:
            # If parsing fails, return as-is or current time
            return date_str


if __name__ == '__main__':
    # Basic test
    import sys
    if len(sys.argv) > 1:
        parser = TwitterArchiveParser(sys.argv[1])
        tweets = parser.extract_tweets()
        print(f"Extracted {len(tweets)} tweets from archive")

        account = parser.get_account_info()
        if account:
            print(f"Account: @{account.get('username', 'unknown')}")
