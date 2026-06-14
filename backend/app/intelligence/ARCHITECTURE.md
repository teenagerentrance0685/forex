"""
Intelligence OS - Architecture & Implementation Guide

## Philosophy

Robot không hỏi: "MACD có cắt chưa?"
Robot hỏi: "Hiện tại tôi đang hiểu thị trường đến mức nào trước khi mạo hiểm vốn?"

Intelligence OS = "Eyes" of the Trading System

## Core Flow

```
Market Data
    ↓
Context Sources (Social, Market, Document, Repository, Knowledge)
    ↓
Evidence Normalization (EvidenceManager)
    ↓
Context Building (ContextManager)
    ↓
TradingContext Object
    {
        "regime": strong_bull|bull|neutral|bear|strong_bear,
        "session": asia|london|newyork|overlap,
        "sentiment": extreme_fear|fear|neutral|greed|extreme_greed,
        "news_risk": no_trade|high|medium|low,
        "memory_score": 0.0-1.0,  # Historical success rate
        "confidence": 0.0-1.0,
    }
    ↓
Downstream Systems:
- NO_TRADE_ENGINE (block risky trades)
- REGIME detector
- CAPITAL_ENGINE (position sizing)
- Memory (store trade+context)
- Evolution (pattern discovery)
```

## Components

### 1. EvidenceManager
**Role**: Normalize all data sources into standardized Evidence schema

Evidence Object:
```python
{
    "source": str,  # reddit, twitter, fed_calendar, github, paper_title
    "evidence_type": str,  # market|social|document|repository|knowledge
    "content": str,
    "confidence": 0.0-1.0,
    "timestamp": datetime,
    "tags": list,  # bullish, bearish, high_impact, etc.
    "metadata": dict,
}
```

### 2. SentimentAnalyzer
**Role**: Extract sentiment from text

Output:
```python
{
    "sentiment": "bullish|bearish|neutral",
    "score": -1.0 to 1.0,
    "confidence": 0.0-1.0,
}
```

### 3. ContextManager
**Role**: Build TradingContext from evidence

Steps:
1. Analyze regime from social sentiment + market data
2. Determine current trading session (Asia|London|NY)
3. Extract sentiment from social sources
4. Assess news risk from economic calendar
5. Query memory for historical success rate
6. Calculate overall confidence

Output: TradingContext object

### 4. IntelligenceManager
**Role**: Orchestrate entire Intelligence OS

Responsibilities:
- Receive evidence from all sources
- Update context periodically (default: 5 min intervals)
- Provide context to downstream systems
- Check trading safety
- Generate risk assessments

## Integration Points

### With NO_TRADE_ENGINE
```python
intelligence = get_intelligence_manager()
if intelligence.is_safe_to_trade():
    # Proceed to regime detection
    pass
else:
    # NO_TRADE_ENGINE blocks all orders
    pass
```

### With Memory System
```python
# When storing a trade
trade_memory = {
    "trade": trade_data,
    "context": intelligence.get_current_context().to_dict(),
    "result": "winner|loser",
    "pnl": float,
}
memory.save_trade_context(trade_memory)
```

### With Evolution System
```python
# When training new strategies
similar_contexts = memory.query_by_context(current_context)
# Find patterns that worked in similar contexts
successful_patterns = filter_by_result(similar_contexts, "winner")
# Use for evolution
```

## Memory Upgrade

**Before Intelligence OS**:
```
Trade → Result → Memory
```

**After Intelligence OS**:
```
Trade + Context → Result → Memory
```

Example saved trade:
```python
{
    "timestamp": "2026-06-14T10:30:00",
    "regime": "strong_bull",
    "session": "london",
    "sentiment": "fear",
    "news_risk": "medium",
    "memory_score": 0.72,
    "entry_price": 1.1050,
    "exit_price": 1.1075,
    "pnl": 25,
    "result": "winner",
    "hold_minutes": 15,
}
```

This enables:
1. **Pattern Discovery**: Find contexts where robot wins most
2. **Regime-Specific Strategies**: Learn what works in different contexts
3. **Adaptive Evolution**: Update strategies based on current context

## Evolution Upgrade

**Before**:
```
Trade → Memory → Evolution
```

**After**:
```
Trade + Context → Memory → Pattern Discovery → Evolution
```

New insights:
- "In strong bull + greed, breakout strategy wins 73% of time"
- "In bear + fear, mean reversion works better"
- "London session has different characteristics than Asia"

## Constraints (✓ = can do, ✗ = cannot do)

Intelligence OS responsibilities:
✓ Create context
✓ Create evidence
✓ Create research summaries
✓ Support memory tagging
✓ Provide confidence scores

**NOT responsible for** (enforce these):
✗ NOT placing orders
✗ NOT modifying execution
✗ NOT bypassing governance
✗ NOT bypassing no_trade_engine

## Usage Example

```python
from backend.app.intelligence import IntelligenceManager

# Initialize
intelligence = IntelligenceManager(update_interval_seconds=300)

# Feed data
intelligence.add_social_intelligence(
    source="reddit",
    content="Bitcoin breaking out!",
    confidence=0.72,
    tags=["bullish", "breakout"],
)

intelligence.add_market_intelligence(
    source="economic_calendar",
    content="Fed announcement in 30 min",
    confidence=0.99,
    tags=["high_impact"],
)

# Get context
context = intelligence.get_current_context()
print(f"Regime: {context.regime.value}")
print(f"Sentiment: {context.sentiment.value}")
print(f"News Risk: {context.news_risk.value}")
print(f"Safe to Trade: {context.is_safe_to_trade()}")

# Get risk assessment
assessment = intelligence.get_risk_assessment()
print(f"Risk Level: {assessment['risk_level']}")
print(f"Reasoning: {assessment['reasoning']}")
```

## Testing

Run tests:
```bash
cd backend
source .venv/bin/activate
pytest app/intelligence/tests/test_intelligence.py -v
```

## Next Steps

1. **Social Intelligence**: Implement Reddit/Twitter readers with API
2. **Market Intelligence**: Connect to real economic calendar APIs
3. **Document Intelligence**: Add PDF parsing and RAG
4. **Repository Intelligence**: GitHub strategy scanner
5. **Knowledge Intelligence**: Embeddings and vector search
6. **Memory Integration**: Save trades with context
7. **Evolution Integration**: Pattern-based strategy updates
"""
