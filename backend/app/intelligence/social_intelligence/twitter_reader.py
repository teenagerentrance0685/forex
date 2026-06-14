"""
Twitter Data Source - Extract trading sentiment from Twitter.

Key accounts to monitor:
- Major trading influencers
- Financial news accounts
- Central bank officials
- Forex/crypto strategists

Note: Requires Twitter API credentials for real implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class Tweet:
    """Tweet with sentiment analysis."""
    tweet_id: str
    author: str
    text: str
    created_at: datetime
    likes: int
    retweets: int
    sentiment: str  # bullish | bearish | neutral
    confidence: float
    symbols_mentioned: List[str]
    is_verified: bool


class TwitterReader:
    """
    Extract trading sentiment from Twitter.
    
    Note: Requires Tweepy or similar for real implementation.
    This is a template showing the interface.
    """

    # Key trading/finance accounts to monitor
    FOREX_ACCOUNTS = [
        "fxempire", "DavidEckleberry", "RichardDennisS", "timothysykes",
        "TradingTicker", "MarkCBroadley",
    ]
    
    CRYPTO_ACCOUNTS = [
        "Cointelegraph", "CryptoTradersUK", "elonmusk", "aantonop",
    ]
    
    FINANCE_ACCOUNTS = [
        "CNBCFastMoney", "MarketWatch", "WSJ", "CNBC", "BBCWorld",
    ]

    # Hashtags to monitor
    TRADING_HASHTAGS = [
        "#forex", "#trading", "#daytrading", "#crypto", "#bitcoin",
        "#ethereum", "#stocks", "#market", "#bull", "#bear",
    ]

    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize Twitter reader.
        
        Args:
            bearer_token: Twitter API v2 bearer token
        """
        self.bearer_token = bearer_token
        self.client = None  # Would be initialized with tweepy
        self.all_accounts = self.FOREX_ACCOUNTS + self.CRYPTO_ACCOUNTS + self.FINANCE_ACCOUNTS

    def read_recent_tweets(
        self,
        limit: int = 100,
        hashtags: Optional[List[str]] = None,
    ) -> List[Tweet]:
        """
        Read recent tweets from trading accounts.
        
        Args:
            limit: Max tweets
            hashtags: Specific hashtags to search
            
        Returns:
            List of tweets with sentiment
        """
        tweets = []
        
        # TODO: Implement with Tweepy:
        # import tweepy
        # client = tweepy.Client(bearer_token=self.bearer_token)
        # 
        # query = " OR ".join(self.TRADING_HASHTAGS)
        # response = client.search_recent_tweets(query=query, max_results=limit)
        # 
        # for tweet in response.data:
        #     tweet_obj = self._analyze_tweet(tweet)
        #     tweets.append(tweet_obj)
        
        return tweets

    def get_trending_sentiment(self) -> Dict[str, Any]:
        """
        Get overall market sentiment from tweets.
        
        Returns:
            {
                "sentiment": "bullish|bearish|neutral",
                "confidence": 0.0-1.0,
                "bullish_tweets": int,
                "bearish_tweets": int,
                "neutral_tweets": int,
                "trending_topics": [...],
                "key_influencers": [...],
            }
        """
        tweets = self.read_recent_tweets(limit=200)
        
        if not tweets:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "bullish_tweets": 0,
                "bearish_tweets": 0,
                "neutral_tweets": 0,
                "trending_topics": [],
                "key_influencers": [],
            }
        
        bullish_count = sum(1 for t in tweets if t.sentiment == "bullish")
        bearish_count = sum(1 for t in tweets if t.sentiment == "bearish")
        neutral_count = sum(1 for t in tweets if t.sentiment == "neutral")
        
        total = len(tweets)
        
        # Determine overall sentiment
        if bullish_count > total * 0.6:
            overall = "bullish"
        elif bearish_count > total * 0.6:
            overall = "bearish"
        else:
            overall = "neutral"
        
        # Calculate confidence
        max_sentiment = max(bullish_count, bearish_count, neutral_count)
        confidence = max_sentiment / total if total > 0 else 0.0
        
        # Get most influential tweets
        influential = sorted(
            tweets,
            key=lambda t: t.likes + t.retweets * 2,
            reverse=True
        )[:5]
        
        return {
            "sentiment": overall,
            "confidence": confidence,
            "bullish_tweets": bullish_count,
            "bearish_tweets": bearish_count,
            "neutral_tweets": neutral_count,
            "tweet_volume": total,
            "influential_tweets": [
                {
                    "author": t.author,
                    "text": t.text[:100],
                    "sentiment": t.sentiment,
                    "engagement": t.likes + t.retweets,
                }
                for t in influential
            ],
        }

    def monitor_account(self, account: str, hours_back: int = 24) -> Dict[str, Any]:
        """
        Monitor specific account's tweets.
        
        Args:
            account: Twitter handle
            hours_back: How far back to look
            
        Returns:
            Account analysis
        """
        tweets = self.read_recent_tweets(limit=50)
        tweets = [t for t in tweets if t.author == account]
        
        if not tweets:
            return {"account": account, "tweets_found": 0}
        
        bullish = sum(1 for t in tweets if t.sentiment == "bullish")
        bearish = sum(1 for t in tweets if t.sentiment == "bearish")
        
        return {
            "account": account,
            "tweets_found": len(tweets),
            "bullish": bullish,
            "bearish": bearish,
            "recent_tweets": [
                {
                    "text": t.text[:150],
                    "sentiment": t.sentiment,
                    "engagement": t.likes + t.retweets,
                }
                for t in tweets[:5]
            ],
        }

    def _analyze_tweet(self, tweet: Any) -> Tweet:
        """Analyze a tweet for sentiment."""
        text = tweet.text.lower()
        
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
        
        # Extract symbols
        symbols = self._extract_symbols(text)
        
        return Tweet(
            tweet_id=tweet.id,
            author=tweet.author_id,
            text=tweet.text,
            created_at=tweet.created_at,
            likes=tweet.public_metrics.get("like_count", 0),
            retweets=tweet.public_metrics.get("retweet_count", 0),
            sentiment=sentiment,
            confidence=confidence,
            symbols_mentioned=symbols,
            is_verified=getattr(tweet, "verified", False),
        )

    @staticmethod
    def _score_sentiment(text: str, sentiment_type: str) -> float:
        """Score sentiment of tweet."""
        bullish_keywords = [
            "bull", "bullish", "moon", "pump", "buy", "long",
            "strong", "surge", "breakout", "rally", "bullrun",
        ]
        bearish_keywords = [
            "bear", "bearish", "crash", "dump", "sell", "short",
            "weak", "decline", "breakdown", "plunge", "crash",
        ]
        
        keywords = bullish_keywords if sentiment_type == "bullish" else bearish_keywords
        
        score = 0.0
        for keyword in keywords:
            count = text.count(keyword)
            score += count * 0.15
        
        return min(1.0, score)

    @staticmethod
    def _extract_symbols(text: str) -> List[str]:
        """Extract trading symbols from text."""
        import re
        
        symbols = []
        
        # Look for symbol patterns
        pattern = r'\$[A-Z]{1,5}|#[A-Z]{3,6}'
        matches = re.findall(pattern, text.upper())
        
        # Clean up
        for match in matches:
            symbol = match.replace("$", "").replace("#", "")
            if symbol not in ["THAT", "THE", "BUT", "AND"]:  # Filter common words
                symbols.append(symbol)
        
        return list(set(symbols))


# Mock implementation for testing
class MockTwitterReader(TwitterReader):
    """Mock Twitter reader for testing."""
    
    def read_recent_tweets(self, limit: int = 100, hashtags: Optional[List[str]] = None) -> List[Tweet]:
        """Return mock tweets."""
        return [
            Tweet(
                tweet_id="mock_t1",
                author="@forex_trader",
                text="EURUSD breaking out! Very bullish momentum incoming $EURUSD #forex",
                created_at=datetime.now(timezone.utc),
                likes=1500,
                retweets=450,
                sentiment="bullish",
                confidence=0.88,
                symbols_mentioned=["EURUSD"],
                is_verified=True,
            ),
            Tweet(
                tweet_id="mock_t2",
                author="@market_news",
                text="Fed chair signals more rate hikes - bearish for growth stocks $SPX #market",
                created_at=datetime.now(timezone.utc),
                likes=3200,
                retweets=1100,
                sentiment="bearish",
                confidence=0.82,
                symbols_mentioned=["SPX"],
                is_verified=True,
            ),
            Tweet(
                tweet_id="mock_t3",
                author="@crypto_analyst",
                text="Bitcoin consolidating near support level $BTC #crypto #trading",
                created_at=datetime.now(timezone.utc),
                likes=680,
                retweets=210,
                sentiment="neutral",
                confidence=0.65,
                symbols_mentioned=["BTC"],
                is_verified=False,
            ),
        ]
