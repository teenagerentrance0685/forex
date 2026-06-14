"""
Complete Integration Example - How all components work together.

Shows full flow:
1. Intelligence OS gathers evidence from all sources
2. Context Manager builds trading context
3. NO_TRADE_ENGINE checks if trading is safe
4. Memory Integration saves trade with context
5. Evolution Integration discovers patterns
6. Next trade uses improved context
"""

from datetime import datetime, timezone
from backend.app.intelligence.intelligence_manager import IntelligenceManager
from backend.app.intelligence.memory_integration import MemoryIntegration, ContextualTrade
from backend.app.intelligence.evolution_integration import EvolutionIntegration
from backend.app.intelligence.no_trade_integration import NoTradeIntegration
from backend.app.intelligence.social_intelligence.reddit_reader import MockRedditReader
from backend.app.intelligence.social_intelligence.twitter_reader import MockTwitterReader
from backend.app.intelligence.market_intelligence.economic_calendar_reader import EconomicCalendarReader
from backend.app.memory.memory_manager import MemoryManager
from backend.app.evolution.manager import EvolutionManager


def example_complete_flow():
    """
    Complete trading cycle:
    1. Gather intelligence
    2. Build context
    3. Check if safe to trade
    4. Save trade with context
    5. Learn from results
    """
    
    print("\n" + "="*70)
    print("COMPLETE INTELLIGENCE OS FLOW")
    print("="*70)
    
    # ============================================================
    # STEP 1: Initialize all systems
    # ============================================================
    print("\n[1] Initializing systems...")
    
    intelligence = IntelligenceManager(update_interval_seconds=300)
    memory_manager = MemoryManager()
    evolution_manager = EvolutionManager(memory_path=memory_manager.root)
    
    memory_integration = MemoryIntegration(memory_manager)
    evolution_integration = EvolutionIntegration(evolution_manager, memory_manager)
    no_trade_integration = NoTradeIntegration()
    
    reddit = MockRedditReader()
    twitter = MockTwitterReader()
    calendar = EconomicCalendarReader()
    
    print("✓ Systems initialized")
    
    # ============================================================
    # STEP 2: Gather intelligence from multiple sources
    # ============================================================
    print("\n[2] Gathering intelligence from all sources...")
    
    # Social Intelligence
    print("  • Reading Reddit...")
    reddit_sentiment = reddit.get_market_sentiment()
    intelligence.add_social_intelligence(
        source="reddit",
        content=f"Overall sentiment: {reddit_sentiment['overall_sentiment']}",
        confidence=reddit_sentiment["confidence"],
        tags=["reddit", reddit_sentiment["overall_sentiment"]],
    )
    
    print("  • Reading Twitter...")
    twitter_sentiment = twitter.get_trending_sentiment()
    intelligence.add_social_intelligence(
        source="twitter",
        content=f"Trending: {twitter_sentiment['sentiment']}",
        confidence=twitter_sentiment["confidence"],
        tags=["twitter", twitter_sentiment["sentiment"]],
    )
    
    # Market Intelligence
    print("  • Checking economic calendar...")
    calendar_summary = calendar.format_event_summary()
    intelligence.add_market_intelligence(
        source="economic_calendar",
        content=f"Events: {calendar_summary['total_events_24h']}",
        confidence=0.95,
        tags=["calendar", f"critical:{calendar_summary['critical_events']}"],
    )
    
    print("✓ Intelligence gathered")
    
    # ============================================================
    # STEP 3: Build trading context
    # ============================================================
    print("\n[3] Building trading context...")
    
    context = intelligence.get_current_context(force_rebuild=True)
    print(f"  • Regime: {context.regime.value}")
    print(f"  • Session: {context.session.value}")
    print(f"  • Sentiment: {context.sentiment.value}")
    print(f"  • News Risk: {context.news_risk.value}")
    print(f"  • Memory Score: {context.memory_score:.2f}")
    print(f"  • Confidence: {context.confidence:.2f}")
    
    # ============================================================
    # STEP 4: Check NO_TRADE_ENGINE
    # ============================================================
    print("\n[4] Checking NO_TRADE_ENGINE...")
    
    permission = no_trade_integration.evaluate_trade_permission(context)
    print(f"  • Permission: {permission['permission']}")
    print(f"  • Approved Size: {permission['approved_size']:.4f} lots")
    print(f"  • Risk Level: {permission['risk_level']}")
    
    if permission['reasons']:
        print(f"  • Reasons: {'; '.join(permission['reasons'][:2])}")
    
    if permission['recommendations']:
        print(f"  • Recommendations: {'; '.join(permission['recommendations'][:1])}")
    
    # Proceed only if not blocked
    if permission['permission'] != 'blocked':
        
        # ============================================================
        # STEP 5: Simulate a trade and save with context
        # ============================================================
        print("\n[5] Executing trade with context awareness...")
        
        trade = ContextualTrade(
            trade_id="trade_001",
            timestamp=datetime.now(timezone.utc),
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
            quantity=permission['approved_size'],
            pnl=25.0,
            pnl_percent=2.26,
            result="WINNER",
            strategy_name="breakout_strategy",
        )
        
        trade_id = memory_integration.save_contextual_trade(trade, context)
        print(f"  ✓ Trade saved with ID: {trade_id}")
        
        # ============================================================
        # STEP 6: Query similar historical contexts
        # ============================================================
        print("\n[6] Learning from similar past trades...")
        
        similar_trades = memory_integration.query_similar_contexts(context, limit=5)
        print(f"  • Found {len(similar_trades)} similar context trades")
        
        if similar_trades:
            winners = sum(1 for t in similar_trades if t.get("result") == "WINNER")
            print(f"  • Win rate in similar contexts: {winners}/{len(similar_trades)}")
        
        # ============================================================
        # STEP 7: Get evolution recommendations
        # ============================================================
        print("\n[7] Evolution recommendations...")
        
        evolution_suggestions = evolution_integration.suggest_evolution(context)
        
        if evolution_suggestions['recommendations']:
            print(f"  • {len(evolution_suggestions['recommendations'])} recommendations:")
            for rec in evolution_suggestions['recommendations'][:2]:
                print(f"    - {rec['type']}: {rec.get('reason', '')[:60]}")
        
        if evolution_suggestions['weaknesses']:
            print(f"  • {len(evolution_suggestions['weaknesses'])} weaknesses detected:")
            for weak in evolution_suggestions['weaknesses'][:1]:
                print(f"    - {weak['weakness']}: {weak['recommendation'][:50]}")
        
        # ============================================================
        # STEP 8: Get context statistics
        # ============================================================
        print("\n[8] Context-based statistics...")
        
        stats = memory_integration.get_context_statistics(
            regime=context.regime.value,
            session=context.session.value,
        )
        
        if stats:
            print(f"  • Total trades in this context: {stats.get('total_trades', 0)}")
            print(f"  • Win rate: {stats.get('win_rate', 0)*100:.1f}%")
            print(f"  • Average P&L: ${stats.get('avg_pnl', 0):.2f}")
        
    else:
        print("\n✗ Trading blocked - NO_TRADE_ENGINE in effect")
        print(f"   Reason: {permission['reasons'][0] if permission['reasons'] else 'Unknown'}")
    
    # ============================================================
    # STEP 9: Final status report
    # ============================================================
    print("\n[9] Final Status Report")
    print("-" * 70)
    
    status = intelligence.get_status()
    print(f"Evidence collected: {status['evidence_count']}")
    print(f"Context age: {status['last_context_update']}")
    print(f"Update interval: {status['update_interval_seconds']}s")
    
    print("\n" + "="*70)
    print("FLOW COMPLETE - Robot understands market before risking capital")
    print("="*70 + "\n")


def example_daily_evolution():
    """
    Example: Daily evolution cycle.
    
    1. Morning: Gather overnight intelligence
    2. Pre-market: Build context for the day
    3. During market: Save trades with context
    4. End of day: Analyze patterns
    5. Overnight: Generate improvements
    """
    
    print("\n" + "="*70)
    print("DAILY EVOLUTION CYCLE")
    print("="*70)
    
    memory_manager = MemoryManager()
    evolution_manager = EvolutionManager(memory_path=memory_manager.root)
    evolution_integration = EvolutionIntegration(evolution_manager, memory_manager)
    
    intelligence = IntelligenceManager()
    
    print("\n[MORNING] Gather overnight intelligence...")
    print("  • Updates: Reddit posts, Twitter trends")
    print("  • Context built for today")
    
    print("\n[TRADING HOURS] Execute with context awareness...")
    print("  • Every trade tagged with context")
    print("  • NO_TRADE_ENGINE blocks risky periods")
    print("  • 50 trades executed today")
    
    print("\n[END OF DAY] Analyze today's performance...")
    
    context = intelligence.get_current_context()
    stats = {
        "total_trades": 50,
        "win_count": 32,
        "loss_count": 18,
        "win_rate": 0.64,
        "best_trade": 125.5,
        "worst_trade": -85.0,
    }
    
    print(f"  • Win rate today: {stats['win_rate']*100:.1f}%")
    print(f"  • Best trade: ${stats['best_trade']:.2f}")
    print(f"  • Worst trade: ${stats['worst_trade']:.2f}")
    
    print("\n[OVERNIGHT] Generate evolution...")
    
    suggestions = evolution_integration.suggest_evolution(context)
    print(f"  • Recommendations: {len(suggestions['recommendations'])} improvements")
    print(f"  • Weaknesses detected: {len(suggestions['weaknesses'])}")
    print(f"  • New patterns discovered: 5")
    
    print("\n[NEXT DAY] Robot uses evolved strategies...")
    print("  • Better suited for today's market")
    print("  • Learns from yesterday's context")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    example_complete_flow()
    example_daily_evolution()
