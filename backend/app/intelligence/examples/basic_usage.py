"""
Example: Using Intelligence OS

Shows how to:
1. Feed evidence from different sources
2. Build trading context
3. Check if safe to trade
4. Integrate with NO_TRADE_ENGINE
"""

from backend.app.intelligence.intelligence_manager import IntelligenceManager
from backend.app.intelligence.social_intelligence.sentiment_analyzer import (
    SentimentAnalyzer,
)


def example_basic_usage():
    """Basic example of Intelligence OS usage."""

    # Initialize Intelligence Manager
    intelligence = IntelligenceManager(update_interval_seconds=300)

    # Add social intelligence
    intelligence.add_social_intelligence(
        source="reddit",
        content="Bitcoin breaking out! Very bullish momentum, moon incoming!",
        confidence=0.72,
        tags=["bullish", "breakout"],
    )

    # Add market intelligence
    intelligence.add_market_intelligence(
        source="economic_calendar",
        content="US Fed Rate Decision coming in 2 hours - HIGH IMPACT",
        confidence=0.95,
        tags=["fed", "rates", "high_impact"],
    )

    # Add document intelligence
    intelligence.add_document_intelligence(
        source="research_paper",
        content="Study shows mean reversion in ranging markets with 72% accuracy",
        confidence=0.68,
        tags=["mean_reversion", "research"],
    )

    # Add repository intelligence
    intelligence.add_repository_intelligence(
        source="github:quantdinger/strategies",
        content="New momentum strategy with 1.8 Sharpe ratio uploaded",
        confidence=0.65,
        tags=["strategy", "momentum"],
    )

    # Get current trading context
    context = intelligence.get_current_context()

    print("\n=== TRADING CONTEXT ===")
    print(f"Regime: {context.regime.value}")
    print(f"Session: {context.session.value}")
    print(f"Sentiment: {context.sentiment.value}")
    print(f"News Risk: {context.news_risk.value}")
    print(f"Memory Score: {context.memory_score:.2f}")
    print(f"Overall Confidence: {context.confidence:.2f}")
    print(f"Risk Level: {context.get_risk_level()}")
    print(f"Safe to Trade: {context.is_safe_to_trade()}")

    # Get full risk assessment
    assessment = intelligence.get_risk_assessment()
    print("\n=== RISK ASSESSMENT ===")
    print(f"Safe to Trade: {assessment['safe_to_trade']}")
    print(f"Risk Level: {assessment['risk_level']}")
    print(f"Reasoning: {assessment['reasoning']}")

    # Get evidence summary
    summary = intelligence.get_evidence_summary()
    print("\n=== EVIDENCE SUMMARY ===")
    print(f"Total Evidence: {summary['total_evidence']}")
    print(f"By Type: {summary['by_type']}")
    print(f"Average Confidence: {summary['average_confidence']:.2f}")


def example_sentiment_analyzer():
    """Example of sentiment analyzer."""

    analyzer = SentimentAnalyzer()

    texts = [
        "Bitcoin is going to the moon! Very bullish breakdown!",
        "Market crash incoming, total collapse, everyone selling!",
        "The market seems to be moving sideways today",
    ]

    print("\n=== SENTIMENT ANALYSIS ===")
    for text in texts:
        result = analyzer.analyze(text)
        print(f"\nText: '{text}'")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Confidence: {result['confidence']:.2f}")


def example_context_flow():
    """Show complete context flow from market to decision."""

    intelligence = IntelligenceManager()

    # Simulate market data input
    print("\n=== CONTEXT FLOW ===")
    print("1. Market Event: Fed announces surprise rate hike")
    intelligence.add_market_intelligence(
        source="news_wire",
        content="Federal Reserve announces emergency rate hike of 0.5%",
        confidence=0.99,
        tags=["fed", "critical"],
    )

    print("2. Social Reaction: Community fears hitting Twitter")
    intelligence.add_social_intelligence(
        source="twitter",
        content="Fed rate hike causing market panic! Everyone is selling!",
        confidence=0.85,
        tags=["fear", "panic"],
    )

    print("3. Build Context...")
    context = intelligence.get_current_context(force_rebuild=True)

    print("4. Evaluate Trading Safety...")
    safe = intelligence.is_safe_to_trade()

    print("\n=== DECISION ===")
    if safe:
        print("✓ SAFE: Proceed with trading based on context")
    else:
        print("✗ BLOCKED: Trading unsafe - NO_TRADE_ENGINE should block orders")

    print(f"\nContext: {context.to_dict()}")


if __name__ == "__main__":
    example_basic_usage()
    example_sentiment_analyzer()
    example_context_flow()
