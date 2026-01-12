# Xhungus Tweet Normalization Schema

All ingestion paths (archive or API) MUST output this internal schema.

## Required Fields
- tweet_id: string
- created_at: ISO-8601 datetime
- text: string (verbatim)
- url: string
- author_handle: string
- source: twitter-archive | x-api

## Optional Fields
- conversation_id
- in_reply_to_tweet_id
- referenced_tweets: [reply | retweet | quote]
- hashtags: []
- mentions: []
- urls: []
- media_ids: []
- language

## Integrity Rules
- Text must never be rewritten
- Normalization must be idempotent
- Missing data is preferred over inferred data
