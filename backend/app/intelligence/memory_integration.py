"""
Memory Integration - Save trades with context for pattern discovery.

Memory Upgrade:
Before: Trade → Result → Memory
After: Trade + Context → Result → Memory → Pattern Discovery

Each trade is tagged with:
- regime (strong_bull | bull | neutral | bear | strong_bear)
- session (asia | london | newyork | overlap)
- sentiment (extreme_fear | fear | neutral | greed | extreme_greed)
- news_risk (no_trade | high | medium | low)
- memory_score (historical success rate in similar contexts)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List

from backend.app.memory.memory_manager import MemoryManager
from backend.app.intelligence.context_manager import TradingContext


@dataclass
class ContextualTrade:
    """Trade record with full context."""

    trade_id: str
    timestamp: datetime

    # Context dimensions
    regime: str
    session: str
    sentiment: str
    news_risk: str
    memory_score: float
    context_confidence: float

    # Trade details
    symbol: str
    direction: str  # BUY | SELL
    entry_price: float
    exit_price: float
    quantity: float = 1.0
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    duration_minutes: Optional[int] = None

    # Results
    pnl: float = 0.0
    pnl_percent: float = 0.0
    result: str = "PENDING"  # WINNER | LOSER | PENDING
    risk_reward_ratio: Optional[float] = None

    # Additional metadata
    strategy_name: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "trade_id": self.trade_id,
            "timestamp": self.timestamp.isoformat(),
            "regime": self.regime,
            "session": self.session,
            "sentiment": self.sentiment,
            "news_risk": self.news_risk,
            "memory_score": self.memory_score,
            "context_confidence": self.context_confidence,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "quantity": self.quantity,
            "duration_minutes": self.duration_minutes,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "result": self.result,
            "risk_reward_ratio": self.risk_reward_ratio,
            "strategy_name": self.strategy_name,
            "notes": self.notes,
        }


class MemoryIntegration:
    """
    Integrate Intelligence OS with Memory System.

    Saves every trade with its context for:
    1. Pattern discovery (what contexts produce winners)
    2. Regime-specific learning (what works in bull vs bear)
    3. Session analysis (which sessions are more profitable)
    4. Risk assessment (which contexts have higher drawdowns)
    """

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def save_contextual_trade(
        self,
        trade: ContextualTrade,
        context: TradingContext,
    ) -> str:
        """
        Save a trade with its trading context.

        Args:
            trade: Trade data
            context: Trading context from Intelligence OS

        Returns:
            Memory ID
        """
        memory_content = {
            "trade": trade.to_dict(),
            "context": context.to_dict(),
            "context_aligned": self._check_context_alignment(trade, context),
        }

        # Determine tags
        tags = self._build_tags(trade, context)

        # Save to memory
        memory_record = self.memory_manager._record(
            content=memory_content,
            memory_type="long_term",
            tags=tags,
        )

        # Persist
        self.memory_manager._write(
            subdir="winners" if trade.result == "WINNER" else "failures",
            data=memory_record.to_dict(),
        )

        return memory_record.memory_id

    def query_similar_contexts(
        self,
        context: TradingContext,
        limit: int = 10,
    ) -> List[ContextualTrade]:
        """
        Find historical trades in similar contexts.

        Args:
            context: Current trading context
            limit: Max results

        Returns:
            List of similar trades
        """
        # Load all records
        records = self.memory_manager._load_persisted_records()

        similar_trades = []

        for record in records:
            if "trade" not in record.content or "context" not in record.content:
                continue

            trade_data = record.content["trade"]
            trade_context = record.content["context"]

            # Calculate similarity score
            similarity = self._calculate_context_similarity(
                context.to_dict(),
                trade_context,
            )

            if similarity > 0.7:  # At least 70% similar
                similar_trades.append((similarity, trade_data, record.memory_id))

        # Sort by similarity and return top N
        similar_trades.sort(key=lambda x: x[0], reverse=True)
        return [t[1] for t in similar_trades[:limit]]

    def get_context_statistics(
        self,
        regime: Optional[str] = None,
        session: Optional[str] = None,
        sentiment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get performance statistics for specific contexts.

        Returns:
            {
                "win_rate": 0.65,
                "avg_pnl": 25.5,
                "total_trades": 100,
                "max_drawdown": -150,
                "best_trade": 500,
                "worst_trade": -300,
            }
        """
        records = self.memory_manager._load_persisted_records()

        relevant_trades = []

        for record in records:
            if "trade" not in record.content or "context" not in record.content:
                continue

            trade_data = record.content["trade"]
            trade_context = record.content["context"]

            # Filter by context
            if regime and trade_context.get("regime") != regime:
                continue
            if session and trade_context.get("session") != session:
                continue
            if sentiment and trade_context.get("sentiment") != sentiment:
                continue

            relevant_trades.append(trade_data)

        if not relevant_trades:
            return {}

        # Calculate statistics
        winners = [t for t in relevant_trades if t.get("result") == "WINNER"]
        losers = [t for t in relevant_trades if t.get("result") == "LOSER"]

        pnls = [t.get("pnl", 0) for t in relevant_trades]

        return {
            "total_trades": len(relevant_trades),
            "win_count": len(winners),
            "loss_count": len(losers),
            "win_rate": len(winners) / len(relevant_trades) if relevant_trades else 0.0,
            "avg_pnl": sum(pnls) / len(pnls) if pnls else 0.0,
            "total_pnl": sum(pnls),
            "max_pnl": max(pnls) if pnls else 0.0,
            "min_pnl": min(pnls) if pnls else 0.0,
            "context_filter": {
                "regime": regime,
                "session": session,
                "sentiment": sentiment,
            },
        }

    def _build_tags(self, trade: ContextualTrade, context: TradingContext) -> List[str]:
        """Build tags for memory record."""
        tags = [
            f"regime:{context.regime.value}",
            f"session:{context.session.value}",
            f"sentiment:{context.sentiment.value}",
            f"news_risk:{context.news_risk.value}",
            f"result:{trade.result.lower()}",
            f"symbol:{trade.symbol}",
            f"direction:{trade.direction.upper()}",
        ]

        if trade.result == "WINNER":
            tags.append("winner")
        else:
            tags.append("loser")

        if trade.pnl_percent > 5:
            tags.append("high_profit")
        elif trade.pnl_percent < -5:
            tags.append("high_loss")

        return tags

    def _calculate_context_similarity(
        self,
        context1: Dict[str, Any],
        context2: Dict[str, Any],
    ) -> float:
        """Calculate similarity between two contexts (0.0 to 1.0)."""
        similarity = 0.0
        match_count = 0

        # Compare dimensions
        dimensions = ["regime", "session", "sentiment", "news_risk"]

        for dim in dimensions:
            match_count += 1
            if context1.get(dim) == context2.get(dim):
                similarity += 1.0

        # Memory score proximity (within 0.1)
        ms1 = context1.get("memory_score", 0.5)
        ms2 = context2.get("memory_score", 0.5)
        match_count += 1
        if abs(ms1 - ms2) <= 0.1:
            similarity += 1.0
        else:
            similarity += max(0, 1.0 - abs(ms1 - ms2))

        return similarity / match_count if match_count > 0 else 0.0

    def _check_context_alignment(
        self,
        trade: ContextualTrade,
        context: TradingContext,
    ) -> Dict[str, Any]:
        """Check if trade was aligned with context."""
        return {
            "regime_match": trade.regime == context.regime.value,
            "session_match": trade.session == context.session.value,
            "sentiment_match": trade.sentiment == context.sentiment.value,
            "result_aligned_with_sentiment": (
                (
                    trade.result == "WINNER"
                    and trade.sentiment in ["greed", "extreme_greed"]
                )
                or (
                    trade.result == "WINNER"
                    and trade.sentiment in ["fear", "extreme_fear"]
                    and trade.result == "WINNER"
                )
            ),
        }
