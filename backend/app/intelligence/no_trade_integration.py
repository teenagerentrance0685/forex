"""
NO_TRADE_ENGINE Integration - Context-aware trading restrictions.

Integration Points:
1. Add context-based blocking rules
2. Block trades during high-risk contexts
3. Reduce position size in uncertain contexts
4. Enforce news risk awareness

Rules:
- NO_TRADE if news_risk == "no_trade"
- NO_TRADE if sentiment == extreme_fear && regime == strong_bear
- REDUCE_SIZE if confidence < 0.5
- MONITOR if memory_score < 0.4
"""

from typing import Dict, Any, Optional
from enum import Enum

from backend.app.intelligence.context_manager import TradingContext


class TradePermission(Enum):
    """Trade permission levels."""
    ALLOWED = "allowed"
    REDUCED_SIZE = "reduced_size"  # 50% of normal
    MONITOR_ONLY = "monitor_only"  # No trading, just analysis
    BLOCKED = "blocked"  # Complete block


class ContextRiskLevel(Enum):
    """Risk level based on context."""
    SAFE = "safe"
    CAUTION = "caution"
    RISKY = "risky"
    EXTREME = "extreme"


class NoTradeIntegration:
    """
    Integrate Intelligence OS with NO_TRADE_ENGINE.
    
    Purpose: Block or restrict trading based on context awareness.
    
    Constraints:
    ✓ Can block/restrict trades
    ✓ Can reduce position size
    ✗ Cannot bypass governance
    ✗ Cannot place orders
    """

    def __init__(self):
        self.context_rules = self._initialize_rules()

    def evaluate_trade_permission(
        self,
        context: TradingContext,
        position_size: float = 0.01,  # Default 0.01 lots
    ) -> Dict[str, Any]:
        """
        Evaluate if trading is permitted given context.
        
        Args:
            context: Current trading context
            position_size: Requested position size
            
        Returns:
            {
                "permission": "allowed|reduced_size|monitor_only|blocked",
                "approved_size": float,
                "reasons": [list of reasons],
                "risk_level": "safe|caution|risky|extreme",
                "recommendations": [list of recommendations],
            }
        """
        reasons = []
        recommendations = []
        approved_size = position_size
        
        # Check news risk first (critical blocker)
        if context.news_risk.value == "no_trade":
            return {
                "permission": TradePermission.BLOCKED.value,
                "approved_size": 0.0,
                "reasons": ["News risk level is NO_TRADE"],
                "risk_level": ContextRiskLevel.EXTREME.value,
                "recommendations": ["Wait for news event to pass"],
            }
        
        # Check extreme contexts
        if (context.sentiment.value == "extreme_fear" and 
            context.regime.value == "strong_bear"):
            return {
                "permission": TradePermission.BLOCKED.value,
                "approved_size": 0.0,
                "reasons": ["Extreme fear in strong bear market - too risky"],
                "risk_level": ContextRiskLevel.EXTREME.value,
                "recommendations": [
                    "Wait for market to stabilize",
                    "Consider defensive strategies only",
                ],
            }
        
        if (context.sentiment.value == "extreme_greed" and 
            context.regime.value == "strong_bull"):
            reasons.append("Extreme greed in strong bull - high risk of reversal")
            recommendations.append("Use tighter stops")
        
        # Check confidence
        if context.confidence < 0.4:
            approved_size = position_size * 0.5
            reasons.append("Low context confidence - reducing size by 50%")
            recommendations.append("Increase evidence gathering")
        elif context.confidence < 0.6:
            approved_size = position_size * 0.75
            reasons.append("Medium context confidence - reducing size by 25%")
        
        # Check memory score (historical success)
        if context.memory_score < 0.4:
            approved_size = approved_size * 0.8
            reasons.append("Low historical success in similar contexts")
            recommendations.append("Adjust strategy for this context")
        elif context.memory_score < 0.5:
            reasons.append("Below average performance in similar contexts")
        
        # Check news risk
        if context.news_risk.value == "high":
            approved_size = approved_size * 0.8
            reasons.append("High impact economic events upcoming")
            recommendations.append("Reduce position size during news")
        elif context.news_risk.value == "medium":
            reasons.append("Moderate economic news risk")
            recommendations.append("Monitor for sudden moves")
        
        # Determine permission level
        if approved_size == 0.0:
            permission = TradePermission.BLOCKED
            risk_level = ContextRiskLevel.EXTREME
        elif approved_size < position_size * 0.5:
            permission = TradePermission.REDUCED_SIZE
            risk_level = ContextRiskLevel.RISKY
        elif approved_size < position_size * 0.9:
            permission = TradePermission.REDUCED_SIZE
            risk_level = ContextRiskLevel.CAUTION
        else:
            # Safe to trade with normal position
            permission = TradePermission.ALLOWED
            if context.confidence > 0.8 and context.memory_score > 0.65:
                risk_level = ContextRiskLevel.SAFE
            else:
                risk_level = ContextRiskLevel.CAUTION
        
        return {
            "permission": permission.value,
            "approved_size": max(0.0, approved_size),
            "size_multiplier": approved_size / position_size if position_size > 0 else 0.0,
            "requested_size": position_size,
            "reasons": reasons,
            "risk_level": risk_level.value,
            "recommendations": recommendations,
        }

    def get_session_restrictions(self, context: TradingContext) -> Dict[str, Any]:
        """
        Get trading restrictions by session.
        
        Different sessions have different characteristics:
        - Asia: Low volatility, trending
        - London: Volatile, news-prone
        - NY: Very active, mean-reverting
        """
        session = context.session.value
        
        restrictions = {
            "asia": {
                "allowed": True,
                "max_spread_pips": 5,
                "preferred_strategy": "trend_following",
                "caution": "Low liquidity near session start",
            },
            "london": {
                "allowed": True,
                "max_spread_pips": 3,
                "preferred_strategy": "breakout",
                "caution": "High volatility, economic news risk",
            },
            "newyork": {
                "allowed": True,
                "max_spread_pips": 2,
                "preferred_strategy": "mean_reversion",
                "caution": "Very active, reversals common",
            },
            "overlap_london_ny": {
                "allowed": True,
                "max_spread_pips": 2,
                "preferred_strategy": "scalping",
                "caution": "Highest volatility, best liquidity",
            },
        }
        
        return restrictions.get(session, restrictions["london"])

    def get_sentiment_adjustments(self, context: TradingContext) -> Dict[str, Any]:
        """
        Get strategy adjustments for different sentiment levels.
        """
        sentiment = context.sentiment.value
        
        adjustments = {
            "extreme_fear": {
                "position_multiplier": 0.5,
                "stop_loss_pips": 15,
                "take_profit_pips": 25,
                "strategy": "contrarian",
                "confidence": "Low - risky",
            },
            "fear": {
                "position_multiplier": 0.75,
                "stop_loss_pips": 12,
                "take_profit_pips": 20,
                "strategy": "defensive",
                "confidence": "Medium",
            },
            "neutral": {
                "position_multiplier": 1.0,
                "stop_loss_pips": 10,
                "take_profit_pips": 15,
                "strategy": "normal",
                "confidence": "Normal",
            },
            "greed": {
                "position_multiplier": 0.9,
                "stop_loss_pips": 12,
                "take_profit_pips": 18,
                "strategy": "trend_follow",
                "confidence": "Medium",
            },
            "extreme_greed": {
                "position_multiplier": 0.5,
                "stop_loss_pips": 15,
                "take_profit_pips": 20,
                "strategy": "reversal",
                "confidence": "Low - reversal risk",
            },
        }
        
        return adjustments.get(sentiment, adjustments["neutral"])

    def format_decision(self, permission_data: Dict[str, Any]) -> str:
        """
        Format decision for NO_TRADE_ENGINE output.
        """
        permission = permission_data["permission"]
        approved_size = permission_data["approved_size"]
        multiplier = permission_data["size_multiplier"]
        
        if permission == TradePermission.BLOCKED.value:
            return f"NO_TRADE: {'; '.join(permission_data['reasons'])}"
        elif permission == TradePermission.REDUCED_SIZE.value:
            return (f"REDUCED_SIZE: {multiplier*100:.0f}% of normal "
                   f"({permission_data['reasons'][0] if permission_data['reasons'] else ''})")
        elif permission == TradePermission.MONITOR_ONLY.value:
            return f"MONITOR_ONLY: {'; '.join(permission_data['reasons'])}"
        else:
            return "ALLOWED: Trading permitted"

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize context-based trading rules."""
        return {
            "no_trade_contexts": [
                {"sentiment": "extreme_fear", "regime": "strong_bear"},
                {"news_risk": "no_trade"},
                {"confidence": "<0.3"},
            ],
            "reduced_size_contexts": [
                {"confidence": "<0.6"},
                {"memory_score": "<0.5"},
                {"news_risk": "high"},
            ],
            "session_rules": {
                "asia": {"min_trades_per_day": 0, "max_position_size": 0.1},
                "london": {"min_trades_per_day": 0, "max_position_size": 0.15},
                "newyork": {"min_trades_per_day": 0, "max_position_size": 0.2},
            },
        }
