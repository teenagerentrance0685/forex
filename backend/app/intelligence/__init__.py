"""
Intelligence OS - Context-Aware Trading Module

Philosophy: Robot needs "eyes" to understand market context before risking capital.

Instead of asking "MACD cut?", the system asks:
"How well do I understand the market before risking capital?"

Core Components:
- Social Intelligence: Community sentiment
- Market Intelligence: Economic calendar & news
- Document Intelligence: Research papers & books
- Repository Intelligence: GitHub strategies
- Knowledge Intelligence: RAG & embeddings
- Evidence Manager: Normalize all data
- Context Manager: Create trading context
- Intelligence Manager: Orchestrate everything

Integrations:
- Memory Integration: Save trades with context for pattern discovery
- Evolution Integration: Generate context-specific improvements
- NO_TRADE Integration: Context-aware trade blocking/restriction
- Data Sources: Reddit, Twitter, Economic Calendar readers

Memory Upgrade:
Every trade is saved with its context (regime, session, sentiment, news, result)

Evolution Upgrade:
Pattern discovery from trades + context → better evolution
"""

from .intelligence_manager import (
    IntelligenceManager,
    get_intelligence_manager,
    initialize_intelligence,
)
from .context_manager import (
    ContextManager,
    TradingContext,
    MarketRegime,
    TradingSession,
    SentimentLevel,
    NewsRiskLevel,
)
from .evidence_manager import EvidenceManager, Evidence, EvidenceType, ConfidenceLevel
from .memory_integration import MemoryIntegration, ContextualTrade
from .evolution_integration import EvolutionIntegration, ContextualPattern
from .no_trade_integration import NoTradeIntegration, TradePermission, ContextRiskLevel

__all__ = [
    # Core
    "IntelligenceManager",
    "get_intelligence_manager",
    "initialize_intelligence",
    "ContextManager",
    "EvidenceManager",
    "Evidence",
    "EvidenceType",
    "ConfidenceLevel",
    # Integrations
    "MemoryIntegration",
    "ContextualTrade",
    "EvolutionIntegration",
    "ContextualPattern",
    "NoTradeIntegration",
    "TradePermission",
    # Context models
    "TradingContext",
    "MarketRegime",
    "TradingSession",
    "SentimentLevel",
    "NewsRiskLevel",
    "ContextRiskLevel",
]
