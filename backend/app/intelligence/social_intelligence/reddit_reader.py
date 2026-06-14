"""
Reddit Data Source - Extract sentiment from trading communities.

Popular subreddits:
- r/forex
- r/Daytrading
- r/investing
- r/trading
- r/stocks
- r/cryptocurrency (for crypto pairs)

Sentiment keywords tracked to detect market mood shifts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import re
from dataclasses import dataclass


@dataclass
class RedditPost:
    """Reddit post with sentiment."""
    post_id: str
    title: str
    content: str
    subreddit: str
    upvotes: int
    sentiment: str  # bullish | bearish | neutral
    confidence: float
    timestamp: datetime
    symbols_mentioned: List[str]


class RedditReader:
    """
    Extract trading sentiment from Reddit.
    
    Note: Requires PRAW (Python Reddit API Wrapper) for real implementation.
    This is a template showing the interface.
    """

    # Common forex/trading symbols mentioned on Reddit
    TRADING_SYMBOLS = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF",
        "BTC", "ETH", "SPX", "SPY", "QQQ", "DXY",
        "GOLD", "OIL", "CRUDE",
    ]

    def __init__(self, subreddits: Optional[List[str]] = None):
        """
        Initialize Reddit reader.
        
        Args:
            subreddits: List of subreddits to monitor (default: popular trading ones)
        """
        self.subreddits = subreddits or [
            "forex", "Daytrading", "investing", "trading", "stocks"
        ]
        self.reddit = None  # Would be initialized with PRAW credentials
        
    def read_recent_posts(self, limit: int = 50) -> List[RedditPost]:
        """
        Read recent posts from trading subreddits.
        
        Args:
            limit: Max posts per subreddit
            
        Returns:
            List of posts with sentiment
        """
        posts = []
        
        # TODO: Implement with PRAW:
        # import praw
        # reddit = praw.Reddit(
        #     client_id='...',
        #     client_secret='...',
        #     user_agent='...'
        # )
        
        for subreddit_name in self.subreddits:
            # subreddit = reddit.subreddit(subreddit_name)
            # for submission in subreddit.new(limit=limit):
            #     post = self._analyze_post(submission)
            #     posts.append(post)
            pass
        
        return posts

    def get_market_sentiment(self) -> Dict[str, Any]:
        """
        Aggregate sentiment from recent posts.
        
        Returns:
            {
                "overall_sentiment": "bullish|bearish|neutral",
                "confidence": 0.0-1.0,
                "bullish_count": int,
                "bearish_count": int,
                "neutral_count": int,
                "symbols_mentioned": {...},
                "top_posts": [...],
            }
        """
        posts = self.read_recent_posts(limit=100)
        
        if not posts:
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.0,
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "symbols_mentioned": {},
                "top_posts": [],
            }
        
        bullish_count = sum(1 for p in posts if p.sentiment == "bullish")
        bearish_count = sum(1 for p in posts if p.sentiment == "bearish")
        neutral_count = sum(1 for p in posts if p.sentiment == "neutral")
        
        total = len(posts)
        
        # Determine overall sentiment
        if bullish_count > total * 0.6:
            overall = "bullish"
        elif bearish_count > total * 0.6:
            overall = "bearish"
        else:
            overall = "neutral"
        
        # Calculate confidence (based on consensus)
        max_sentiment = max(bullish_count, bearish_count, neutral_count)
        confidence = max_sentiment / total if total > 0 else 0.0
        
        # Track mentioned symbols
        symbols_mentioned = {}
        for post in posts:
            for symbol in post.symbols_mentioned:
                symbols_mentioned[symbol] = symbols_mentioned.get(symbol, 0) + 1
        
        return {
            "overall_sentiment": overall,
            "confidence": confidence,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "symbols_mentioned": symbols_mentioned,
            "top_posts": [
                {
                    "title": p.title[:100],
                    "sentiment": p.sentiment,
                    "upvotes": p.upvotes,
                    "subreddit": p.subreddit,
                }
                for p in sorted(posts, key=lambda p: p.upvotes, reverse=True)[:5]
            ],
        }

    def _analyze_post(self, submission: Any) -> Optional[RedditPost]:
        """Analyze a Reddit post for sentiment."""
        text = (submission.title + " " + submission.selftext).lower()
        
        # Extract sentiment
        bullish_score = self._score_sentiment(text, "bullish")
        bearish_score = self._score_sentiment(text, "bearish")
        
        if bullish_score > bearish_score:
            sentiment = "bullish"
            confidence = bullish_score
        elif bearish_score > bullish_score:
            sentiment = "bearish"
            confidence = bearish_score
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        # Extract symbols mentioned
        symbols = self._extract_symbols(text)
        
        return RedditPost(
            post_id=submission.id,
            title=submission.title,
            content=submission.selftext[:500],
            subreddit=submission.subreddit.display_name,
            upvotes=submission.score,
            sentiment=sentiment,
            confidence=confidence,
            timestamp=datetime.fromtimestamp(submission.created_utc, timezone.utc),
            symbols_mentioned=symbols,
        )

    @staticmethod
    def _score_sentiment(text: str, sentiment_type: str) -> float:
        """Score sentiment of text."""
        bullish_keywords = [
            "bull", "bullish", "moon", "pump", "buy", "long",
            "strong", "surge", "breakout", "rally", "gains",
        ]
        bearish_keywords = [
            "bear", "bearish", "crash", "dump", "sell", "short",
            "weak", "decline", "breakdown", "plunge", "loss",
        ]
        
        keywords = bullish_keywords if sentiment_type == "bullish" else bearish_keywords
        
        score = 0.0
        for keyword in keywords:
            count = text.count(keyword)
            score += count * 0.1
        
        return min(1.0, score)

    @staticmethod
    def _extract_symbols(text: str) -> List[str]:
        """Extract trading symbols from text."""
        symbols = []
        
        # Look for symbol patterns like EURUSD, BTC, SPY
        pattern = r'\b([A-Z]{3,6})\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if match in RedditReader.TRADING_SYMBOLS:
                symbols.append(match)
        
        return list(set(symbols))  # Unique symbols


# Mock implementation for testing without PRAW
class MockRedditReader(RedditReader):
    """Mock Reddit reader for testing."""
    
    def read_recent_posts(self, limit: int = 50) -> List[RedditPost]:
        """Return mock posts."""
        return [
            RedditPost(
                post_id="mock1",
                title="Bitcoin breaking out - MASSIVE bullish momentum",
                content="Bulls taking over, this is huge!",
                subreddit="investing",
                upvotes=1250,
                sentiment="bullish",
                confidence=0.85,
                timestamp=datetime.now(timezone.utc),
                symbols_mentioned=["BTC", "SPY"],
            ),
            RedditPost(
                post_id="mock2",
                title="Fed rate hike fears - market crash incoming",
                content="Everyone selling, this is bearish AF",
                subreddit="trading",
                upvotes=850,
                sentiment="bearish",
                confidence=0.75,
                timestamp=datetime.now(timezone.utc),
                symbols_mentioned=["DXY", "SPX"],
            ),
            RedditPost(
                post_id="mock3",
                title="EURUSD ranging today",
                content="Sideways action, not much happening",
                subreddit="forex",
                upvotes=120,
                sentiment="neutral",
                confidence=0.6,
                timestamp=datetime.now(timezone.utc),
                symbols_mentioned=["EURUSD"],
            ),
        ]
