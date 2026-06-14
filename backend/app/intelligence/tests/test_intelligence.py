"""
Tests for Intelligence OS.

Tests:
1. Evidence Manager
2. Context Manager
3. Intelligence Manager integration
"""

import pytest
from datetime import datetime, timedelta

from backend.app.intelligence.evidence_manager import (
    EvidenceManager, Evidence, EvidenceType, ConfidenceLevel
)
from backend.app.intelligence.context_manager import (
    ContextManager, TradingContext, MarketRegime, SentimentLevel, NewsRiskLevel
)
from backend.app.intelligence.intelligence_manager import IntelligenceManager
from backend.app.intelligence.social_intelligence.sentiment_analyzer import SentimentAnalyzer


class TestEvidenceManager:
    """Test evidence manager functionality."""

    def test_add_evidence(self):
        """Test adding evidence."""
        manager = EvidenceManager()
        
        evidence = manager.add_evidence(
            source="reddit",
            evidence_type=EvidenceType.SOCIAL,
            content="Bitcoin is bullish",
            confidence=0.75,
            tags=["bullish"],
        )
        
        assert evidence.source == "reddit"
        assert evidence.confidence == 0.75
        assert len(manager.evidence_store) == 1

    def test_confidence_validation(self):
        """Test that confidence must be 0.0-1.0."""
        manager = EvidenceManager()
        
        with pytest.raises(ValueError):
            manager.add_evidence(
                source="test",
                evidence_type=EvidenceType.SOCIAL,
                content="test",
                confidence=1.5,  # Invalid
            )

    def test_get_recent_evidence(self):
        """Test getting recent evidence."""
        manager = EvidenceManager()
        
        # Add multiple evidence
        for i in range(5):
            manager.add_evidence(
                source=f"source_{i}",
                evidence_type=EvidenceType.SOCIAL,
                content=f"content_{i}",
                confidence=0.5,
            )
        
        recent = manager.get_recent_evidence(limit=3)
        assert len(recent) == 3
        # Should be sorted by timestamp descending
        assert recent[0].timestamp >= recent[1].timestamp

    def test_high_confidence_filter(self):
        """Test filtering by confidence."""
        manager = EvidenceManager()
        
        manager.add_evidence("s1", EvidenceType.SOCIAL, "c1", 0.9)
        manager.add_evidence("s2", EvidenceType.SOCIAL, "c2", 0.5)
        manager.add_evidence("s3", EvidenceType.SOCIAL, "c3", 0.3)
        
        high_conf = manager.get_high_confidence_evidence(min_confidence=0.7)
        assert len(high_conf) == 1
        assert high_conf[0].confidence == 0.9

    def test_tags_filter(self):
        """Test filtering by tags."""
        manager = EvidenceManager()
        
        manager.add_evidence("s1", EvidenceType.SOCIAL, "c1", 0.5, tags=["bullish"])
        manager.add_evidence("s2", EvidenceType.SOCIAL, "c2", 0.5, tags=["bearish"])
        manager.add_evidence("s3", EvidenceType.SOCIAL, "c3", 0.5, tags=["bullish", "strong"])
        
        bullish = manager.get_evidence_by_tags(["bullish"])
        assert len(bullish) == 2


class TestSentimentAnalyzer:
    """Test sentiment analyzer."""

    def test_bullish_sentiment(self):
        """Test bullish sentiment detection."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("Bitcoin moon! Super bullish breakout!")
        assert result["sentiment"] == "bullish"
        assert result["score"] > 0.2

    def test_bearish_sentiment(self):
        """Test bearish sentiment detection."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("Market crash! Very bearish decline!")
        assert result["sentiment"] == "bearish"
        assert result["score"] < -0.2

    def test_neutral_sentiment(self):
        """Test neutral sentiment."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("The market moved today")
        assert result["sentiment"] == "neutral"


class TestContextManager:
    """Test context manager."""

    def test_build_context(self):
        """Test building context from evidence."""
        manager = EvidenceManager()
        context_mgr = ContextManager(manager)
        
        # Add some evidence
        manager.add_evidence("s1", EvidenceType.SOCIAL, "bullish", 0.8)
        manager.add_evidence("s2", EvidenceType.MARKET, "no_important_news", 0.6)
        
        context = context_mgr.build_context()
        
        assert context.regime is not None
        assert context.session is not None
        assert context.sentiment is not None
        assert context.news_risk is not None

    def test_context_safety_check(self):
        """Test trading safety evaluation."""
        manager = EvidenceManager()
        context_mgr = ContextManager(manager)
        
        # Build safe context
        context = context_mgr.build_context()
        
        # Should generally be safe without high-risk evidence
        if context.news_risk.value != "no_trade":
            assert context.confidence > 0.3  # Should have some confidence

    def test_risk_level_assessment(self):
        """Test risk level calculation."""
        manager = EvidenceManager()
        context_mgr = ContextManager(manager)
        
        context = context_mgr.build_context()
        risk = context.get_risk_level()
        
        assert risk in ["low", "medium", "high"]


class TestIntelligenceManager:
    """Test main Intelligence Manager."""

    def test_initialization(self):
        """Test Intelligence Manager init."""
        manager = IntelligenceManager()
        
        assert manager.evidence_manager is not None
        assert manager.context_manager is not None
        assert manager.current_context is None

    def test_add_evidence_methods(self):
        """Test adding different types of evidence."""
        manager = IntelligenceManager()
        
        manager.add_social_intelligence("reddit", "bullish", 0.7)
        manager.add_market_intelligence("calendar", "fed_event", 0.9)
        manager.add_document_intelligence("paper", "research", 0.6)
        manager.add_repository_intelligence("github", "strategy", 0.65)
        manager.add_knowledge_intelligence("rag", "insight", 0.72)
        
        summary = manager.get_evidence_summary()
        assert summary["total_evidence"] == 5

    def test_get_current_context(self):
        """Test getting current context."""
        manager = IntelligenceManager()
        
        context = manager.get_current_context()
        assert context is not None
        assert context.regime is not None

    def test_is_safe_to_trade(self):
        """Test trading safety check."""
        manager = IntelligenceManager()
        
        # Without evidence, should be relatively safe
        safe = manager.is_safe_to_trade()
        assert isinstance(safe, bool)

    def test_risk_assessment(self):
        """Test risk assessment output."""
        manager = IntelligenceManager()
        
        assessment = manager.get_risk_assessment()
        
        assert "safe_to_trade" in assessment
        assert "risk_level" in assessment
        assert "context" in assessment
        assert "reasoning" in assessment

    def test_evidence_cleanup(self):
        """Test old evidence cleanup."""
        manager = IntelligenceManager()
        
        # Add evidence
        manager.add_social_intelligence("s1", "c1", 0.5)
        manager.add_social_intelligence("s2", "c2", 0.5)
        
        assert len(manager.evidence_manager.evidence_store) == 2
        
        # Cleanup (with 0 hours threshold, should remove everything)
        removed = manager.cleanup_old_evidence(hours=0)
        assert removed == 2

    def test_status_report(self):
        """Test complete status report."""
        manager = IntelligenceManager()
        manager.add_social_intelligence("s1", "c1", 0.7)
        
        status = manager.get_status()
        
        assert "timestamp" in status
        assert "context" in status
        assert "evidence_count" in status
        assert "evidence_summary" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
