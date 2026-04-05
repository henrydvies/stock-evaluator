from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Protocol

import os

class RedditProviderError(Exception):
    pass

@dataclass
class RedditMention:
    id: str
    symbol: str
    created_utc: datetime
    subreddit: str
    source_type: str # post/ comment
    text: str
    score: int
    num_comments: Optional[int] = None
    permalink: str
    
class RedditProvider(Protocol):
    async def fetch_mentions(self, symbol: str, lookback_days: int, limit: int = 1000) -> List[RedditMention]:
        """
        Fetch mentions on reddit for a given stock symbol.

        Args:
            symbol (str): The stock symbol to fetch mentions for.
            lookback_days (int): The number of days to look back for mentions.
            limit (int, optional): The maximum number of mentions to fetch. Defaults to 1000.

        Returns:
            List[RedditMention]: A list of RedditMention objects representing the mentions of the given stock symbol.
        """
        ...
        
@dataclass
class AsyncPrawRedditProvider:
    client_id: str = field(default_factory=lambda: os.getenv("CLIENT_ID"))
    client_secret: str = field(default_factory=lambda: os.getenv("CLIENT_SECRET"))
    user_agent: str = "StockSentimentBot"
    
    # Define subreddits to monitor for stock mentions
    subreddits: List[str] = field(default_factory=lambda: [
        "wallstreetbets",
        "stocks",
        "investing",
        "StockMarket",
        "SecurityAnalysis",
        "ValueInvesting",
        "pennystocks",
        "SmallCap",
    ])
    
    include_comments: bool = True
    max_comments_per_post: int = 25
    
    async def fetch_mentions(
        self,
        symbol: str,
        lookback_days: int,
        limit: int = 1000,
    ) -> List[RedditMention]:
        """Fetch mentions on reddit for a given stock symbol."""
        if not self.client_id or not self.client_secret:
            raise RedditProviderError("Reddit client_id and client_secret must be set in environment variables.")

        if lookback_days <= 0:
            raise RedditProviderError("lookback_days must be a positive integer.")
        
        if limit <= 0:
            return []
        
        try:
            import asyncpraw
        except Exception as e:
            raise RedditProviderError(f"Failed to import asyncpraw: {e}")
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)  
        symbol_upper = symbol.upper()
        queries = [f"{symbol_upper}", f"${symbol_upper}"]
        
        mentions_by_id: dict[str, RedditMention] = {}
        
        try:
            reddit = asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
            
            # Go through alloed subreddits looking for mentions
            for sub_name in self.subreddits:
                if len(mentions_by_id) >= limit:
                    break
                
                subreddit = await reddit.subreddit(sub_name)
                
                # Check for both the symbol and $symbol
                for q in queries:
                    if len(mentions_by_id) >= limit:
                        break
                    
                    async for submission in subreddit.search(
                        q, 
                        sort="new",
                        time_filter="month",
                        limit=limit * 2,  # Fetch more to account for filtering by date and duplicates
                    ):
                        # As 7d/ 30d filters, 1 month covers 30d, but not the 7d so this does ensure
                        created = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                        if created < cutoff: 
                            continue
                        
                        text = f"{submission.title}\n{submission.selftext or ''}".strip()
                        if text and submission.id not in mentions_by_id:
                            mentions_by_id[submission.id] = RedditMention(
                                id=submission.id,
                                symbol=symbol_upper,
                                created_utc=created,
                                subreddit=sub_name,
                                source_type="post",
                                text=text,
                                score=int(submission.score or 0),
                                num_comments=int(submission.num_comments or 0),
                                permalink=f"https://reddit.com{submission.permalink}",
                            )
                    if self.include_comments and len(mentions_by_id) < limit:
                        await submission.comments.replace_more(limit=0)
                        comments_seen = 0
                        
                        for comment in submission.comments.list():
                            if comments_seen >= self.max_comments_per_post:
                                break
                            
                            c_created = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                            
                            if c_created < cutoff:
                                continue
                            
                            body = (comment.body or "").strip()
                            if not body or body in ("[deleted]", "[removed]"):
                                continue
                            
                            body_upper = body.upper()
                            if symbol_upper in body_upper or f"${symbol_upper}" in body_upper:
                                continue
                            
                            key = f"c_{comment.id}"
                            if key not in mentions_by_id:
                                mentions_by_id[key] = RedditMention(
                                    id=key,
                                    symbol=symbol_upper,
                                    created_utc=c_created,
                                    subreddit=sub_name,
                                    source_type="comment",
                                    text=body,
                                    score=int(comment.score or 0),
                                    permalink=f"https://reddit.com{comment.permalink}",
                                )
                                comments_seen += 1
                    if len(mentions_by_id) >= limit:
                        break
                        
            await reddit.close()
            
            return sorted(mentions_by_id.values(), key=lambda m: m.created_utc, reverse=True)
            
        except Exception as e:
            raise RedditProviderError(f"Failed fetching Reddit mentions for '{symbol_upper}': {e}")