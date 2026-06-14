"""
Integration Tests - Verify all components work together.

Tests:
1. Memory Integration - Save and query contextual trades
2. Evolution Integration - Discover patterns and generate recommendations
3. NO_TRADE Integration - Block/restrict trades appropriately
4. Data Sources - Reddit, Twitter, Economic Calendar
"""

import pytest
from datetime import datetime, timedelta

from backend.app.intelligence.intelligence_manager import IntelligenceManager
from backend.app.intelligence.memory_integration import MemoryIntegration, ContextualTrade
from backend.app.intelligence.evolution_integration import EvolutionIntegration
from backend.app.intelligence.no_trade_integration import NoTradeIntegration, TradePermission
from backend.app.intelligence.context_manager import (
    TradingContext, MarketRegime, TradingSession, SentimentLevel, NewsRiskLevel
)
from backend.app.intelligence.social_intelligence.reddit_reader import MockRedditReader
from backend.app.intelligence.social_intelligence.twitter_reader import MockTwitterReader
from backend.app.intelligence.market_intelligence.economic_calendar_reader import (
    EconomicCalendarReader, EventImportance
)
from backend.app.memory.memory_manager import MemoryManager
from backend.app.evolution.manager import EvolutionManager


class TestMemoryIntegration:
    """Test memory integration with Intelligence OS."""

    def test_save_contextual_trade(self):
        """Test saving trade with context."""
        memory_manager = MemoryManager()
        memory_integration = MemoryIntegration(memory_manager)
        
        context = TradingContext(
            regime=MarketRegime.BULL,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.GREED,
            news_risk=NewsRiskLevel.LOW,
            memory_score=0.75,
            confidence=0.85,
            reasoning="Test context",
        )
        
        trade = ContextualTrade(
            trade_id="test_001",
            timestamp=datetime.utcnow(),
            regime="bull",
            session="london",
            sentiment="greed",
            news_risk="low",
            memory_score=0.75,
            context_confidence=0.85,
            symbol="EURUSD",
            direction="BUY",
            entry_price=1.1050,
            exit_price=1.1075,
            pnl=25.0,
            pnl_percent=2.26,
            result="WINNER",
        )
        
        trade_id = memory_integration.save_contextual_trade(trade, context)
        assert trade_id is not None

    def test_query_similar_contexts(self):
        """Test querying similar contexts."""
        memory_manager = MemoryManager()
        memory_integration = MemoryIntegration(memory_manager)
        
        context = TradingContext(
            regime=MarketRegime.BULL,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.GREED,
            news_risk=NewsRiskLevel.LOW,
            memory_score=0.75,
            confidence=0.85,
        )
        
        similar = memory_integration.query_similar_contexts(context)
        # Should return list (possibly empty if no similar trades)
        assert isinstance(similar, list)

    def test_context_statistics(self):
        """Test getting context statistics."""
        memory_manager = MemoryManager()
        memory_integration = MemoryIntegration(memory_manager)
        
        stats = memory_integration.get_context_statistics(
            regime="bull",
            session="london",
        )
        
        assert isinstance(stats, dict)
        if stats:
            assert "total_trades" in stats
            assert "win_rate" in stats


class TestEvolutionIntegration:
    """Test evolution integration."""

    def test_discover_context_patterns(self):
        """Test pattern discovery."""
        memory_manager = MemoryManager()
        evolution_manager = EvolutionManager(memory_path=memory_manager.root)
        evolution_integration = EvolutionIntegration(
            evolution_manager, memory_manager
        )
        
        patterns = evolution_integration.discover_context_patterns(
            regime="bull",
            min_confidence=0.5,
        )
        
        assert isinstance(patterns, list)

    def test_generate_context_recommendations(self):
        """Test generating recommendations."""
        memory_manager = MemoryManager()
        evolution_manager = EvolutionManager(memory_path=memory_manager.root)
        evolution_integration = EvolutionIntegration(
            evolution_manager, memory_manager
        )
        
        context = TradingContext(
            regime=MarketRegime.BULL,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.GREED,
            news_risk=NewsRiskLevel.LOW,
            memory_score=0.75,
            confidence=0.85,
        )
        
        recommendations = evolution_integration.generate_context_recommendations(context)
        assert isinstance(recommendations, list)

    def test_detect_context_weaknesses(self):
        """Test weakness detection."""
        memory_manager = MemoryManager()
        evolution_manager = EvolutionManager(memory_path=memory_manager.root)
        evolution_integration = EvolutionIntegration(
            evolution_manager, memory_manager
        )
        
        context = TradingContext(
            regime=MarketRegime.BEAR,
            session=TradingSession.ASIA,
            sentiment=SentimentLevel.FEAR,
            news_risk=NewsRiskLevel.HIGH,
            memory_score=0.4,
            confidence=0.6,
        )
        
        weaknesses = evolution_integration.detect_context_weaknesses(context)
        assert isinstance(weaknesses, list)


class TestNoTradeIntegration:
    """Test NO_TRADE_ENGINE integration."""

    def test_safe_context_allowed(self):
        """Test that safe contexts allow trading."""
        no_trade = NoTradeIntegration()
        
        context = TradingContext(
            regime=MarketRegime.BULL,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.NEUTRAL,
            news_risk=NewsRiskLevel.LOW,
            memory_score=0.75,
            confidence=0.85,
        )
        
        result = no_trade.evaluate_trade_permission(context)
        assert result['permission'] == TradePermission.ALLOWED.value

    def test_no_trade_news_blocks(self):
        """Test that NO_TRADE news blocks trading."""
        no_trade = NoTradeIntegration()
        
        context = TradingContext(
            regime=MarketRegime.NEUTRAL,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.NEUTRAL,
            news_risk=NewsRiskLevel.NO_TRADE,  # This should block
            memory_score=0.75,
            confidence=0.85,
        )
        
        result = no_trade.evaluate_trade_permission(context)
        assert result['permission'] == TradePermission.BLOCKED.value

    def test_extreme_fear_bear_blocks(self):
        """Test that extreme fear + strong bear blocks trading."""
        no_trade = NoTradeIntegration()
        
        context = TradingContext(
            regime=MarketRegime.STRONG_BEAR,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.EXTREME_FEAR,
            news_risk=NewsRiskLevel.LOW,
            memory_score=0.75,
            confidence=0.85,
        )
        
        result = no_trade.evaluate_trade_permission(context)
        assert result['permission'] == TradePermission.BLOCKED.value

    def test_low_confidence_reduces_size(self):
        """Test that low confidence reduces position size."""
        no_trade = NoTradeIntegration()
        
        context = TradingContext(
            regime=MarketRegime.NEUTRAL,
            session=TradingSession.LONDON,
            sentiment=SentimentLevel.NEUTRAL,
            news_risk=NewsRiskLevel.LOW,
            memory_score=0.75,
            confidence=0.35,  # Low confidence
        )
        
        result = no_trade.evaluate_trade_permission(context, position_size=0.1)
        assert result['permission'] == TradePermission.REDUCED_SIZE.value
        assert result['approved_size'] < 0.1


class TestDataSources:
    """Test data source readers."""

    def test_reddit_reader(self):
        """Test Reddit reader."""
        reddit = MockRedditReader()
        posts = reddit.read_recent_posts()
        
        assert len(posts) > 0
        sentiment = reddit.get_market_sentiment()
        assert "overall_sentiment" in sentiment
        assert sentiment["confidence"] >= 0.0

    def test_twitter_reader(self):
        """Test Twitter reader."""
        twitter = MockTwitterReader()
        tweets = twitter.read_recent_tweets()
        
        assert len(tweets) > 0
        sentiment = twitter.get_trending_sentiment()
        assert "sentiment" in sentiment
        assert sentiment["confidence"] >= 0.0

    def test_economic_calendar(self):
        """Test economic calendar."""
        calendar = EconomicCalendarReader()
        
        # Get upcoming events
        upcoming = calendar.get_upcoming_events(hours_ahead=48)
        assert isinstance(upcoming, list)
        
        # Get critical events
        critical = calendar.get_critical_events_window(minutes_window=60)
        assert isinstance(critical, list)
        
        # Check NO_TRADE decision
        should_block, reason = calendar.should_enter_no_trade_mode()
        assert isinstance(should_block, bool)


class TestCompleteFlow:
    """Test complete integration flow."""

    def test_full_trading_cycle(self):
        """Test complete trading cycle."""
        # Initialize
        intelligence = IntelligenceManager()
        memory_manager = MemoryManager()
        evolution_manager = EvolutionManager(memory_path=memory_manager.root)
        
        memory_integration = MemoryIntegration(memory_manager)
        evolution_integration = EvolutionIntegration(evolution_manager, memory_manager)
        no_trade_integration = NoTradeIntegration()
        
        reddit = MockRedditReader()
        twitter = MockTwitterReader()
        calendar = EconomicCalendarReader()
        
        # Add intelligence from all sources
        reddit_sentiment = reddit.get_market_sentiment()
        intelligence.add_social_intelligence(
            source="reddit",
            content=f"Sentiment: {reddit_sentiment['overall_sentiment']}",
            confidence=reddit_sentiment["confidence"],
        )
        
        twitter_sentiment = twitter.get_trending_sentiment()
        intelligence.add_social_intelligence(
            source="twitter",
            content=f"Trending: {twitter_sentiment['sentiment']}",
            confidence=twitter_sentiment["confidence"],
        )
        
        calendar_summary = calendar.format_event_summary()
        intelligence.add_market_intelligence(
            source="economic_calendar",
            content=f"Events: {calendar_summary['total_events_24h']}",
            confidence=0.95,
        )
        
        # Build context
        context = intelligence.get_current_context()
        assert context is not None
        
        # Check NO_TRADE
        permission = no_trade_integration.evaluate_trade_permission(context)
        assert "permission" in permission
        
        # If allowed, save trade
        if permission['permission'] != 'blocked':
            trade = ContextualTrade(
                trade_id="test_full_001",
                timestamp=datetime.utcnow(),
                regime=context.regime.value,
                session=context.session.value,
                sentiment=context.sentiment.value,
                news_risk=context.news_risk.value,
                memory_score=context.memory_score,
                context_confidence=context.confidence,
                symbol="EURUSD",
                direction="BUY",
                entry_price=1.1050,
                exit_price=1.1075,
                pnl=25.0,
                pnl_percent=2.26,
                result="WINNER",
            )
            
            trade_id = memory_integration.save_contextual_trade(trade, context)
            assert trade_id is not None
            
            # Get evolution suggestions
            suggestions = evolution_integration.suggest_evolution(context)
            assert "recommendations" in suggestions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
