"""
Intelligence Manager - Orchestrate entire Intelligence OS.

The "Eyes" of the Trading System.

Flow:
Context Sources (social, market, document, repository, knowledge)
    ↓
Evidence Manager (normalize all data)
    ↓
Context Manager (build context object)
    ↓
Output: TradingContext
    {
        regime, session, sentiment, news_risk, memory_score, confidence
    }

This context is then fed to:
1. NO_TRADE_ENGINE - block unsafe trades
2. REGIME detector - adjust strategy
3. CAPITAL_ENGINE - position sizing
4. Memory system - context-tagged trade journaling
5. Evolution system - pattern discovery
"""

from datetime import datetime
from typing import Dict, Any, Optional, List

from .evidence_manager import EvidenceManager, EvidenceType, Evidence
from .context_manager import ContextManager, TradingContext


class IntelligenceManager:
    """
    Central orchestrator for Intelligence OS.
    
    Responsible for:
    1. Managing evidence from all sources
    2. Building trading context
    3. Providing context to downstream systems
    4. Updating context periodically
    """

    def __init__(self, update_interval_seconds: int = 300):
        """
        Initialize Intelligence Manager.
        
        Args:
            update_interval_seconds: How often to rebuild context (default 5 min)
        """
        self.evidence_manager = EvidenceManager()
        self.context_manager = ContextManager(self.evidence_manager)
        self.update_interval_seconds = update_interval_seconds
        self.last_context_update: Optional[datetime] = None
        self.current_context: Optional[TradingContext] = None

    def add_social_intelligence(
        self,
        source: str,  # reddit, twitter, youtube
        content: str,
        confidence: float,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        """Add social intelligence evidence."""
        return self.evidence_manager.add_evidence(
            source=source,
            evidence_type=EvidenceType.SOCIAL,
            content=content,
            confidence=confidence,
            tags=tags or [],
        )

    def add_market_intelligence(
        self,
        source: str,  # economic_calendar, news_wire
        content: str,
        confidence: float,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        """Add market intelligence evidence (economic calendar, news)."""
        return self.evidence_manager.add_evidence(
            source=source,
            evidence_type=EvidenceType.MARKET,
            content=content,
            confidence=confidence,
            tags=tags or [],
        )

    def add_document_intelligence(
        self,
        source: str,  # paper_title, book_title
        content: str,
        confidence: float,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        """Add document intelligence evidence (research papers, books)."""
        return self.evidence_manager.add_evidence(
            source=source,
            evidence_type=EvidenceType.DOCUMENT,
            content=content,
            confidence=confidence,
            tags=tags or [],
        )

    def add_repository_intelligence(
        self,
        source: str,  # github_user/repo
        content: str,
        confidence: float,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        """Add repository intelligence evidence (GitHub strategies)."""
        return self.evidence_manager.add_evidence(
            source=source,
            evidence_type=EvidenceType.REPOSITORY,
            content=content,
            confidence=confidence,
            tags=tags or [],
        )

    def add_knowledge_intelligence(
        self,
        source: str,  # rag_result, embeddings_match
        content: str,
        confidence: float,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        """Add knowledge intelligence evidence (RAG, embeddings)."""
        return self.evidence_manager.add_evidence(
            source=source,
            evidence_type=EvidenceType.KNOWLEDGE,
            content=content,
            confidence=confidence,
            tags=tags or [],
        )

    def get_current_context(self, force_rebuild: bool = False) -> TradingContext:
        """
        Get current trading context.
        
        Rebuilds context if:
        1. force_rebuild is True
        2. Current context is None
        3. Update interval has elapsed
        
        Args:
            force_rebuild: Force rebuild even if interval hasn't elapsed
            
        Returns:
            TradingContext object with all dimensions
        """
        now = datetime.utcnow()
        should_rebuild = (
            force_rebuild or
            self.current_context is None or
            (self.last_context_update is None) or
            ((now - self.last_context_update).total_seconds() > self.update_interval_seconds)
        )
        
        if should_rebuild:
            self.current_context = self.context_manager.build_context()
            self.last_context_update = now
        
        return self.current_context

    def is_safe_to_trade(self) -> bool:
        """
        Check if current context is safe for trading.
        
        This is the key integration point with NO_TRADE_ENGINE.
        
        Returns:
            True if trading is permitted, False otherwise
        """
        context = self.get_current_context()
        return context.is_safe_to_trade()

    def get_risk_assessment(self) -> Dict[str, Any]:
        """
        Get comprehensive risk assessment of current context.
        
        Returns:
            {
                "safe_to_trade": bool,
                "risk_level": "low|medium|high",
                "context": {...},
                "reasoning": str,
            }
        """
        context = self.get_current_context()
        return {
            "safe_to_trade": context.is_safe_to_trade(),
            "risk_level": context.get_risk_level(),
            "context": context.to_dict(),
            "reasoning": context.reasoning,
        }

    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get summary of all evidence in system."""
        return self.evidence_manager.get_evidence_summary()

    def get_high_confidence_evidence(
        self,
        min_confidence: float = 0.7,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get high-confidence evidence for research/analysis."""
        evidence = self.evidence_manager.get_high_confidence_evidence(
            min_confidence=min_confidence
        )
        return [e.to_dict() for e in evidence[:limit]]

    def cleanup_old_evidence(self, hours: int = 24) -> int:
        """Remove evidence older than N hours."""
        return self.evidence_manager.clear_old_evidence(hours=hours)

    def get_status(self) -> Dict[str, Any]:
        """Get complete Intelligence OS status."""
        context = self.get_current_context()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "context": context.to_dict(),
            "evidence_count": len(self.evidence_manager.evidence_store),
            "evidence_summary": self.get_evidence_summary(),
            "last_context_update": (
                self.last_context_update.isoformat()
                if self.last_context_update else None
            ),
            "update_interval_seconds": self.update_interval_seconds,
        }


# Singleton instance (optional - can also create per request)
_intelligence_manager: Optional[IntelligenceManager] = None


def get_intelligence_manager() -> IntelligenceManager:
    """Get or create singleton Intelligence Manager."""
    global _intelligence_manager
    if _intelligence_manager is None:
        _intelligence_manager = IntelligenceManager()
    return _intelligence_manager


def initialize_intelligence(update_interval_seconds: int = 300) -> IntelligenceManager:
    """Initialize Intelligence Manager with custom settings."""
    global _intelligence_manager
    _intelligence_manager = IntelligenceManager(update_interval_seconds)
    return _intelligence_manager
