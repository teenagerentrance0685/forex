"""
Evolution Integration - Use context for pattern discovery and improvement.

Evolution Upgrade:
Before: Trade → Memory → Evolution
After: Trade + Context → Memory → Pattern Discovery → Evolution

New capabilities:
1. Regime-specific evolution (what works in strong_bull vs bear)
2. Session-aware adaptation (London strategies vs Asia)
3. Sentiment-based adjustments (fear trades vs greed trades)
4. Context-conditional improvements (different rules for different contexts)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.evolution.manager import EvolutionManager
from backend.app.memory.memory_manager import MemoryManager
from backend.app.intelligence.context_manager import TradingContext


class ContextualPattern:
    """Pattern specific to a context."""

    def __init__(
        self,
        pattern_name: str,
        regime: str,
        session: str,
        sentiment: str,
        win_count: int,
        loss_count: int,
        avg_pnl: float,
        confidence: float,
    ):
        self.pattern_name = pattern_name
        self.regime = regime
        self.session = session
        self.sentiment = sentiment
        self.win_count = win_count
        self.loss_count = loss_count
        self.avg_pnl = avg_pnl
        self.confidence = confidence

    @property
    def win_rate(self) -> float:
        total = self.win_count + self.loss_count
        return self.win_count / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_name": self.pattern_name,
            "regime": self.regime,
            "session": self.session,
            "sentiment": self.sentiment,
            "win_rate": self.win_rate,
            "avg_pnl": self.avg_pnl,
            "confidence": self.confidence,
        }


class EvolutionIntegration:
    """
    Integrate Intelligence OS with Evolution System.

    Enhanced evolution capabilities:
    1. Discover patterns per context
    2. Generate context-specific strategies
    3. Detect weaknesses in specific contexts
    4. Recommend improvements based on context
    """

    def __init__(
        self,
        evolution_manager: EvolutionManager,
        memory_manager: MemoryManager,
    ):
        self.evolution_manager = evolution_manager
        self.memory_manager = memory_manager

    def discover_context_patterns(
        self,
        regime: Optional[str] = None,
        session: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_confidence: float = 0.6,
    ) -> List[ContextualPattern]:
        """
        Discover patterns specific to context dimensions.

        Args:
            regime: Filter by market regime
            session: Filter by trading session
            sentiment: Filter by sentiment
            min_confidence: Minimum confidence threshold

        Returns:
            List of context-specific patterns
        """
        # Load trade records
        records = self.memory_manager._load_persisted_records()

        patterns_dict: Dict[str, Dict[str, Any]] = {}

        for record in records:
            if "trade" not in record.content or "context" not in record.content:
                continue

            trade_data = record.content["trade"]
            context_data = record.content["context"]

            # Filter by context
            if regime and context_data.get("regime") != regime:
                continue
            if session and context_data.get("session") != session:
                continue
            if sentiment and context_data.get("sentiment") != sentiment:
                continue

            # Build pattern key
            pattern_key = (
                f"{trade_data.get('symbol')}_"
                f"{trade_data.get('strategy_name', 'unknown')}"
            )

            # Aggregate
            if pattern_key not in patterns_dict:
                patterns_dict[pattern_key] = {
                    "regime": context_data.get("regime"),
                    "session": context_data.get("session"),
                    "sentiment": context_data.get("sentiment"),
                    "wins": 0,
                    "losses": 0,
                    "pnls": [],
                }

            if trade_data.get("result") == "WINNER":
                patterns_dict[pattern_key]["wins"] += 1
            else:
                patterns_dict[pattern_key]["losses"] += 1

            patterns_dict[pattern_key]["pnls"].append(trade_data.get("pnl", 0))

        # Create pattern objects
        patterns = []
        for pattern_key, data in patterns_dict.items():
            total = data["wins"] + data["losses"]
            win_rate = data["wins"] / total if total > 0 else 0.0

            # Confidence based on sample size and win rate
            confidence = min(1.0, (total / 30.0) * abs(win_rate - 0.5) * 2)

            if confidence >= min_confidence:
                pattern = ContextualPattern(
                    pattern_name=pattern_key,
                    regime=data.get("regime", "unknown"),
                    session=data.get("session", "unknown"),
                    sentiment=data.get("sentiment", "unknown"),
                    win_count=data["wins"],
                    loss_count=data["losses"],
                    avg_pnl=(
                        sum(data["pnls"]) / len(data["pnls"]) if data["pnls"] else 0.0
                    ),
                    confidence=confidence,
                )
                patterns.append(pattern)

        return sorted(patterns, key=lambda p: p.confidence, reverse=True)

    def generate_context_recommendations(
        self,
        context: TradingContext,
    ) -> List[Dict[str, Any]]:
        """
        Generate improvement recommendations for current context.

        Args:
            context: Current trading context

        Returns:
            List of recommendations
        """
        recommendations = []

        # Find patterns that work in this context
        patterns = self.discover_context_patterns(
            regime=context.regime.value,
            session=context.session.value,
            sentiment=context.sentiment.value,
        )

        # Strong patterns = high confidence + high win rate
        strong_patterns = [
            p for p in patterns if p.win_rate > 0.65 and p.confidence > 0.7
        ]

        for pattern in strong_patterns:
            recommendations.append(
                {
                    "type": "use_pattern",
                    "pattern": pattern.pattern_name,
                    "confidence": pattern.confidence,
                    "win_rate": pattern.win_rate,
                    "avg_pnl": pattern.avg_pnl,
                    "reason": f"High-confidence pattern in {context.regime.value} + "
                    f"{context.session.value} + {context.sentiment.value}",
                }
            )

        # Weak patterns = low win rate
        weak_patterns = [
            p for p in patterns if p.win_rate < 0.45 and p.confidence > 0.5
        ]

        for pattern in weak_patterns:
            recommendations.append(
                {
                    "type": "improve_pattern",
                    "pattern": pattern.pattern_name,
                    "current_win_rate": pattern.win_rate,
                    "confidence": pattern.confidence,
                    "reason": f"Underperforming pattern in {context.regime.value} context",
                }
            )

        # No patterns yet
        if not patterns:
            recommendations.append(
                {
                    "type": "insufficient_data",
                    "confidence": 0.0,
                    "reason": f"Insufficient history for {context.regime.value} + "
                    f"{context.session.value} + {context.sentiment.value}",
                }
            )

        return recommendations

    def detect_context_weaknesses(
        self,
        context: TradingContext,
    ) -> List[Dict[str, Any]]:
        """
        Detect weaknesses specific to current context.

        Args:
            context: Current trading context

        Returns:
            List of detected weaknesses
        """
        weaknesses = []

        # Load statistics
        patterns = self.discover_context_patterns(
            regime=context.regime.value,
            session=context.session.value,
            sentiment=context.sentiment.value,
        )

        total_trades = sum(p.win_count + p.loss_count for p in patterns)
        total_wins = sum(p.win_count for p in patterns)

        # Overall win rate
        overall_win_rate = total_wins / total_trades if total_trades > 0 else 0.0

        # Context is weak if win rate below 50%
        if overall_win_rate < 0.50 and total_trades > 10:
            weaknesses.append(
                {
                    "context": f"{context.regime.value}/{context.session.value}/{context.sentiment.value}",
                    "weakness": "low_win_rate",
                    "win_rate": overall_win_rate,
                    "total_trades": total_trades,
                    "recommendation": "Adjust strategy parameters or trade less in this context",
                    "severity": "high",
                }
            )

        # Extreme drawdowns in this context
        record_pnls = []
        records = self.memory_manager._load_persisted_records()

        for record in records:
            if "trade" not in record.content or "context" not in record.content:
                continue

            if (
                record.content["context"].get("regime") == context.regime.value
                and record.content["context"].get("session") == context.session.value
            ):
                record_pnls.append(record.content["trade"].get("pnl", 0))

        if record_pnls and min(record_pnls) < -200:
            weaknesses.append(
                {
                    "context": context.regime.value,
                    "weakness": "high_drawdown_risk",
                    "worst_trade": min(record_pnls),
                    "recommendation": "Reduce position size in this context",
                    "severity": "medium",
                }
            )

        return weaknesses

    def suggest_evolution(
        self,
        context: TradingContext,
    ) -> Dict[str, Any]:
        """
        Suggest evolution improvements for current context.

        Args:
            context: Current trading context

        Returns:
            Evolution suggestions
        """
        weaknesses = self.detect_context_weaknesses(context)
        recommendations = self.generate_context_recommendations(context)

        return {
            "context": context.to_dict(),
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evolution_ready": len(recommendations) > 0,
        }
