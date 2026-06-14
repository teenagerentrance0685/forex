"""
Sentiment Analyzer - Analyze sentiment from social sources.

Output: "bullish" | "bearish" | "neutral"
Confidence: 0.0 - 1.0
"""

from typing import Dict, Any, Optional
from enum import Enum


class SentimentScore(Enum):
    """Sentiment scoring."""
    VERY_NEGATIVE = -1.0
    NEGATIVE = -0.5
    NEUTRAL = 0.0
    POSITIVE = 0.5
    VERY_POSITIVE = 1.0


class SentimentAnalyzer:
    """Simple sentiment analyzer for trading discussions."""

    # Keywords for bullish sentiment
    BULLISH_KEYWORDS = {
        "bull": 0.3, "bullish": 0.3,
        "moon": 0.4, "pump": 0.3,
        "buy": 0.2, "long": 0.2,
        "strong": 0.2, "surge": 0.3,
        "breakout": 0.25, "rally": 0.3,
    }

    # Keywords for bearish sentiment
    BEARISH_KEYWORDS = {
        "bear": 0.3, "bearish": 0.3,
        "crash": 0.4, "dump": 0.3,
        "sell": 0.2, "short": 0.2,
        "weak": 0.2, "decline": 0.3,
        "breakdown": 0.25, "plunge": 0.3,
    }

    # Intensifiers
    INTENSIFIERS = ["very", "extremely", "super", "mega"]

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Returns:
            {
                "sentiment": "bullish|bearish|neutral",
                "score": -1.0 to 1.0,
                "confidence": 0.0 to 1.0,
                "keywords_found": list,
            }
        """
        text_lower = text.lower()

        # Count keyword occurrences
        bullish_score = self._score_keywords(text_lower, self.BULLISH_KEYWORDS)
        bearish_score = self._score_keywords(text_lower, self.BEARISH_KEYWORDS)

        # Check for intensifiers (increase confidence)
        intensity_multiplier = 1.0
        if any(i in text_lower for i in self.INTENSIFIERS):
            intensity_multiplier = 1.3

        # Calculate net sentiment
        net_score = (bullish_score - bearish_score) * intensity_multiplier
        net_score = max(-1.0, min(1.0, net_score))  # Clamp to [-1, 1]

        # Determine sentiment label
        if net_score > 0.2:
            sentiment = "bullish"
        elif net_score < -0.2:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        # Calculate confidence based on score magnitude
        confidence = abs(net_score)

        return {
            "sentiment": sentiment,
            "score": net_score,
            "confidence": confidence,
        }

    @staticmethod
    def _score_keywords(text: str, keywords: Dict[str, float]) -> float:
        """Score text based on keyword presence."""
        score = 0.0
        for keyword, weight in keywords.items():
            if keyword in text:
                # Count occurrences
                count = text.count(keyword)
                score += weight * count
        return score
