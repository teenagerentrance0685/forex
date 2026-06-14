"""
FastAPI endpoints for Intelligence OS.

Expose Intelligence OS functionality via REST API.

Endpoints:
- POST /api/v1/intelligence/evidence - Add evidence
- GET /api/v1/intelligence/context - Get current trading context
- GET /api/v1/intelligence/risk-assessment - Get risk assessment
- GET /api/v1/intelligence/status - Get full status
- GET /api/v1/intelligence/evidence/summary - Evidence summary
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.app.intelligence.intelligence_manager import get_intelligence_manager
from backend.app.intelligence.evidence_manager import EvidenceType
from backend.app.intelligence.context_manager import (
    MarketRegime, TradingSession, SentimentLevel, NewsRiskLevel
)


# Pydantic Models for API
class AddEvidenceRequest(BaseModel):
    """Add evidence to Intelligence OS."""
    source: str
    evidence_type: str  # social|market|document|repository|knowledge
    content: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class TradingContextResponse(BaseModel):
    """Trading context response."""
    regime: str
    session: str
    sentiment: str
    news_risk: str
    memory_score: float
    confidence: float
    timestamp: str
    reasoning: str


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""
    safe_to_trade: bool
    risk_level: str
    context: Dict[str, Any]
    reasoning: str


# Create router
router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])


@router.post("/evidence/social")
async def add_social_evidence(request: AddEvidenceRequest):
    """Add social intelligence evidence."""
    intelligence = get_intelligence_manager()
    evidence = intelligence.add_social_intelligence(
        source=request.source,
        content=request.content,
        confidence=request.confidence,
        tags=request.tags,
    )
    return {
        "success": True,
        "message": "Social evidence added",
        "evidence_id": id(evidence),
    }


@router.post("/evidence/market")
async def add_market_evidence(request: AddEvidenceRequest):
    """Add market intelligence evidence."""
    intelligence = get_intelligence_manager()
    evidence = intelligence.add_market_intelligence(
        source=request.source,
        content=request.content,
        confidence=request.confidence,
        tags=request.tags,
    )
    return {
        "success": True,
        "message": "Market evidence added",
        "evidence_id": id(evidence),
    }


@router.post("/evidence/document")
async def add_document_evidence(request: AddEvidenceRequest):
    """Add document intelligence evidence."""
    intelligence = get_intelligence_manager()
    evidence = intelligence.add_document_intelligence(
        source=request.source,
        content=request.content,
        confidence=request.confidence,
        tags=request.tags,
    )
    return {
        "success": True,
        "message": "Document evidence added",
        "evidence_id": id(evidence),
    }


@router.post("/evidence/repository")
async def add_repository_evidence(request: AddEvidenceRequest):
    """Add repository intelligence evidence."""
    intelligence = get_intelligence_manager()
    evidence = intelligence.add_repository_intelligence(
        source=request.source,
        content=request.content,
        confidence=request.confidence,
        tags=request.tags,
    )
    return {
        "success": True,
        "message": "Repository evidence added",
        "evidence_id": id(evidence),
    }


@router.post("/evidence/knowledge")
async def add_knowledge_evidence(request: AddEvidenceRequest):
    """Add knowledge intelligence evidence."""
    intelligence = get_intelligence_manager()
    evidence = intelligence.add_knowledge_intelligence(
        source=request.source,
        content=request.content,
        confidence=request.confidence,
        tags=request.tags,
    )
    return {
        "success": True,
        "message": "Knowledge evidence added",
        "evidence_id": id(evidence),
    }


@router.get("/context", response_model=TradingContextResponse)
async def get_context(force_rebuild: bool = False):
    """Get current trading context."""
    intelligence = get_intelligence_manager()
    context = intelligence.get_current_context(force_rebuild=force_rebuild)
    
    return TradingContextResponse(
        regime=context.regime.value,
        session=context.session.value,
        sentiment=context.sentiment.value,
        news_risk=context.news_risk.value,
        memory_score=context.memory_score,
        confidence=context.confidence,
        timestamp=context.timestamp.isoformat(),
        reasoning=context.reasoning,
    )


@router.get("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment():
    """Get comprehensive risk assessment."""
    intelligence = get_intelligence_manager()
    assessment = intelligence.get_risk_assessment()
    
    return RiskAssessmentResponse(
        safe_to_trade=assessment["safe_to_trade"],
        risk_level=assessment["risk_level"],
        context=assessment["context"],
        reasoning=assessment["reasoning"],
    )


@router.get("/safe-to-trade")
async def check_safe_to_trade():
    """Quick check: is it safe to trade?"""
    intelligence = get_intelligence_manager()
    safe = intelligence.is_safe_to_trade()
    
    return {
        "safe_to_trade": safe,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/evidence/summary")
async def get_evidence_summary():
    """Get summary of all evidence."""
    intelligence = get_intelligence_manager()
    summary = intelligence.get_evidence_summary()
    
    return {
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/evidence/high-confidence")
async def get_high_confidence_evidence(min_confidence: float = 0.7, limit: int = 20):
    """Get high-confidence evidence."""
    intelligence = get_intelligence_manager()
    evidence = intelligence.get_high_confidence_evidence(
        min_confidence=min_confidence,
        limit=limit,
    )
    
    return {
        "evidence": evidence,
        "count": len(evidence),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/status")
async def get_status():
    """Get complete Intelligence OS status."""
    intelligence = get_intelligence_manager()
    status = intelligence.get_status()
    
    return status


@router.post("/cleanup-old-evidence")
async def cleanup_old_evidence(hours: int = 24):
    """Remove evidence older than N hours."""
    intelligence = get_intelligence_manager()
    removed = intelligence.cleanup_old_evidence(hours=hours)
    
    return {
        "success": True,
        "removed_count": removed,
        "timestamp": datetime.utcnow().isoformat(),
    }
