"""
Context Manager - Create trading context from evidence sources.

Context Object:
{
    "regime": "strong_bull | bull | neutral | bear | strong_bear",
    "session": "asia | london | newyork | overlap",
    "sentiment": "fear | greed | neutral",
    "news_risk": "high | medium | low | no_trade",
    "memory_score": 0.0-1.0,  # Success rate from historical similar contexts
    "confidence": 0.0-1.0,  # Overall context confidence
}

Context becomes input to:
1. NO_TRADE_ENGINE (block risky trades)
2. REGIME detector
3. CAPITAL_ENGINE (position sizing)
4. Evolution (pattern discovery)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum

from .evidence_manager import Evidence, EvidenceType, EvidenceManager


class MarketRegime(Enum):
    """Market regime classification."""

    STRONG_BULL = "strong_bull"
    BULL = "bull"
    NEUTRAL = "neutral"
    BEAR = "bear"
    STRONG_BEAR = "strong_bear"


class TradingSession(Enum):
    """Trading sessions."""

    ASIA = "asia"  # UTC 0-8
    LONDON = "london"  # UTC 8-16
    NEWYORK = "newyork"  # UTC 13-21
    OVERLAP_LONDON_NY = "overlap_london_ny"  # UTC 13-16
    OVERLAP_ASIA_LONDON = "overlap_asia_london"  # UTC 7-8


class SentimentLevel(Enum):
    """Market sentiment."""

    EXTREME_FEAR = "extreme_fear"
    FEAR = "fear"
    NEUTRAL = "neutral"
    GREED = "greed"
    EXTREME_GREED = "extreme_greed"


class NewsRiskLevel(Enum):
    """Economic news risk."""

    NO_TRADE = "no_trade"  # High impact events upcoming
    HIGH = "high"  # Important events
    MEDIUM = "medium"
    LOW = "low"  # Calm news calendar


@dataclass
class TradingContext:
    """
    Trading context object - input before taking any trade.

    Each field represents a dimension of market understanding:
    - regime: Overall market direction
    - session: Time-of-day factor
    - sentiment: Community mood
    - news_risk: Calendar risk
    - memory_score: Historical success in similar contexts
    - confidence: Overall confidence in this context assessment
    """

    regime: MarketRegime
    session: TradingSession
    sentiment: SentimentLevel
    news_risk: NewsRiskLevel
    memory_score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_ids: List[str] = field(default_factory=list)
    reasoning: str = ""  # Explanation of how context was derived

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for API/storage."""
        return {
            "regime": self.regime.value,
            "session": self.session.value,
            "sentiment": self.sentiment.value,
            "news_risk": self.news_risk.value,
            "memory_score": self.memory_score,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "reasoning": self.reasoning,
        }

    def is_safe_to_trade(self) -> bool:
        """Check if context is safe for trading."""
        # NO_TRADE news risk = block
        if self.news_risk == NewsRiskLevel.NO_TRADE:
            return False

        # Extreme fear + strong bear = risky
        if (
            self.sentiment == SentimentLevel.EXTREME_FEAR
            and self.regime == MarketRegime.STRONG_BEAR
        ):
            return False

        # Low confidence = block
        if self.confidence < 0.5:
            return False

        return True

    def get_risk_level(self) -> str:
        """Classify overall risk of trading in this context."""
        risk_score = 0.0

        # Regime contributes to risk
        regime_risk = {
            MarketRegime.STRONG_BULL: -0.2,  # Lower risk
            MarketRegime.BULL: -0.1,
            MarketRegime.NEUTRAL: 0.0,
            MarketRegime.BEAR: 0.1,
            MarketRegime.STRONG_BEAR: 0.2,  # Higher risk
        }
        risk_score += regime_risk.get(self.regime, 0.0)

        # Sentiment contributes
        sentiment_risk = {
            SentimentLevel.EXTREME_FEAR: 0.3,
            SentimentLevel.FEAR: 0.15,
            SentimentLevel.NEUTRAL: 0.0,
            SentimentLevel.GREED: 0.1,
            SentimentLevel.EXTREME_GREED: 0.25,
        }
        risk_score += sentiment_risk.get(self.sentiment, 0.0)

        # News risk
        news_risk_score = {
            NewsRiskLevel.NO_TRADE: 1.0,
            NewsRiskLevel.HIGH: 0.3,
            NewsRiskLevel.MEDIUM: 0.15,
            NewsRiskLevel.LOW: 0.0,
        }
        risk_score += news_risk_score.get(self.news_risk, 0.0)

        # Normalize by confidence
        risk_score = max(0.0, min(1.0, risk_score)) * (1 - (1 - self.confidence) * 0.5)

        if risk_score < 0.2:
            return "low"
        elif risk_score < 0.5:
            return "medium"
        else:
            return "high"


class ContextManager:
    """
    Builds trading context from evidence sources.

    Flow:
    Evidence (social, market, document, etc.)
        ↓
    Analyze each source
        ↓
    Build context dimensions
        ↓
    Create TradingContext object
        ↓
    Feed to NO_TRADE_ENGINE, REGIME, CAPITAL_ENGINE
    """

    def __init__(self, evidence_manager: EvidenceManager):
        self.evidence_manager = evidence_manager
        self.current_context: Optional[TradingContext] = None

    def build_context(self) -> TradingContext:
        """Build complete trading context from all evidence sources."""
        # Get recent evidence
        evidence = self.evidence_manager.get_recent_evidence(limit=100)

        # Analyze each dimension
        regime = self._analyze_regime(evidence)
        session = self._analyze_session()
        sentiment = self._analyze_sentiment(evidence)
        news_risk = self._analyze_news_risk(evidence)
        memory_score = self._calculate_memory_score(evidence)
        confidence = self._calculate_confidence(evidence, regime, session, sentiment)
        reasoning = self._build_reasoning(regime, session, sentiment, news_risk)

        self.current_context = TradingContext(
            regime=regime,
            session=session,
            sentiment=sentiment,
            news_risk=news_risk,
            memory_score=memory_score,
            confidence=confidence,
            reasoning=reasoning,
        )

        return self.current_context

    def _analyze_regime(self, evidence: List[Evidence]) -> MarketRegime:
        """Analyze market regime from social + market intelligence."""
        # Filter social sentiment evidence
        social_evidence = [
            e for e in evidence if e.evidence_type == EvidenceType.SOCIAL
        ]

        if not social_evidence:
            return MarketRegime.NEUTRAL

        # Calculate weighted sentiment
        bullish_score = sum(
            e.confidence for e in social_evidence if "bull" in e.content.lower()
        )
        bearish_score = sum(
            e.confidence for e in social_evidence if "bear" in e.content.lower()
        )

        diff = bullish_score - bearish_score

        if diff > 0.5:
            return MarketRegime.STRONG_BULL
        elif diff > 0.2:
            return MarketRegime.BULL
        elif diff < -0.5:
            return MarketRegime.STRONG_BEAR
        elif diff < -0.2:
            return MarketRegime.BEAR
        else:
            return MarketRegime.NEUTRAL

    def _analyze_session(self) -> TradingSession:
        """Determine current trading session based on UTC time."""
        now = datetime.now(timezone.utc)
        hour = now.hour

        # Simplified session logic
        if 0 <= hour < 8:
            return TradingSession.ASIA
        elif 8 <= hour < 13:
            return TradingSession.LONDON
        elif 13 <= hour < 16:
            return TradingSession.OVERLAP_LONDON_NY
        elif 16 <= hour < 21:
            return TradingSession.NEWYORK
        else:
            return TradingSession.ASIA

    def _analyze_sentiment(self, evidence: List[Evidence]) -> SentimentLevel:
        """Analyze community sentiment from social intelligence."""
        social_evidence = [
            e for e in evidence if e.evidence_type == EvidenceType.SOCIAL
        ]

        if not social_evidence:
            return SentimentLevel.NEUTRAL

        avg_confidence = sum(e.confidence for e in social_evidence) / len(
            social_evidence
        )

        # Heuristic: higher confidence in social = more extreme sentiment
        if avg_confidence > 0.85:
            fear_count = sum(1 for e in social_evidence if "fear" in e.content.lower())
            greed_count = sum(
                1 for e in social_evidence if "greed" in e.content.lower()
            )

            if fear_count > greed_count:
                return SentimentLevel.EXTREME_FEAR
            else:
                return SentimentLevel.EXTREME_GREED
        elif avg_confidence > 0.7:
            fear_count = sum(1 for e in social_evidence if "fear" in e.content.lower())
            if fear_count > len(social_evidence) * 0.6:
                return SentimentLevel.FEAR
            else:
                return SentimentLevel.GREED

        return SentimentLevel.NEUTRAL

    def _analyze_news_risk(self, evidence: List[Evidence]) -> NewsRiskLevel:
        """Analyze economic calendar and news risk."""
        market_evidence = [
            e for e in evidence if e.evidence_type == EvidenceType.MARKET
        ]

        if not market_evidence:
            return NewsRiskLevel.LOW

        # Check for high-impact news markers
        high_impact = [e for e in market_evidence if e.confidence > 0.85]

        if len(high_impact) > 3:
            return NewsRiskLevel.NO_TRADE
        elif len(high_impact) > 1:
            return NewsRiskLevel.HIGH
        elif market_evidence:
            return NewsRiskLevel.MEDIUM
        else:
            return NewsRiskLevel.LOW

    def _calculate_memory_score(self, evidence: List[Evidence]) -> float:
        """
        Calculate how well we've done in similar contexts before.
        Placeholder: would query memory system for similar trade contexts.
        """
        # TODO: Query memory for similar regime+sentiment+session combinations
        return 0.65  # Default placeholder

    def _calculate_confidence(
        self,
        evidence: List[Evidence],
        regime: MarketRegime,
        session: TradingSession,
        sentiment: SentimentLevel,
    ) -> float:
        """Calculate overall confidence in context assessment."""
        if not evidence:
            return 0.3  # Low confidence if no evidence

        avg_evidence_confidence = sum(e.confidence for e in evidence) / len(evidence)

        # Confidence influenced by:
        # 1. Quality of input evidence
        # 2. Diversity of sources
        source_types = set(e.evidence_type for e in evidence)
        source_diversity = len(source_types) / len(EvidenceType)

        confidence = (avg_evidence_confidence * 0.7) + (source_diversity * 0.3)
        return max(0.0, min(1.0, confidence))

    def _build_reasoning(
        self,
        regime: MarketRegime,
        session: TradingSession,
        sentiment: SentimentLevel,
        news_risk: NewsRiskLevel,
    ) -> str:
        """Build human-readable reasoning."""
        return (
            f"Market regime is {regime.value}. "
            f"Trading session: {session.value}. "
            f"Community sentiment: {sentiment.value}. "
            f"News risk level: {news_risk.value}."
        )
