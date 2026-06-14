"""
Evidence Manager - Normalize all intelligence sources into standardized evidence format.

Evidence flow:
- Source (social, market, document, GitHub) 
  ↓
- Parse & Extract
  ↓
- Normalize to Evidence schema
  ↓
- Store with confidence score
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum


class EvidenceType(Enum):
    """Types of evidence that feed into context."""
    MARKET = "market"  # Economic news, calendar events
    SOCIAL = "social"  # Sentiment from Reddit, Twitter
    DOCUMENT = "document"  # Research papers, books
    REPOSITORY = "repository"  # GitHub strategies
    KNOWLEDGE = "knowledge"  # RAG results
    SYSTEM = "system"  # Internal metrics


class ConfidenceLevel(Enum):
    """Evidence confidence levels."""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.85


@dataclass
class Evidence:
    """Standardized evidence object."""
    source: str  # reddit, twitter, economic_calendar, github, paper_title, etc.
    evidence_type: EvidenceType
    content: str
    confidence: float  # 0.0 - 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate confidence is between 0 and 1."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "evidence_type": self.evidence_type.value,
            "content": self.content,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


class EvidenceManager:
    """
    Centralized evidence normalizer.
    
    Ensures all intelligence sources use consistent schema:
    {
        "source": str,
        "confidence": float,
        "evidence_type": str,
        "content": str,
        "tags": list,
        "timestamp": datetime
    }
    """

    def __init__(self):
        self.evidence_store: List[Evidence] = []

    def add_evidence(
        self,
        source: str,
        evidence_type: EvidenceType,
        content: str,
        confidence: float,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Evidence:
        """Add normalized evidence to store."""
        evidence = Evidence(
            source=source,
            evidence_type=evidence_type,
            content=content,
            confidence=confidence,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.evidence_store.append(evidence)
        return evidence

    def get_recent_evidence(
        self,
        evidence_type: Optional[EvidenceType] = None,
        limit: int = 10,
    ) -> List[Evidence]:
        """Get recent evidence, optionally filtered by type."""
        filtered = self.evidence_store
        if evidence_type:
            filtered = [e for e in filtered if e.evidence_type == evidence_type]
        
        # Sort by timestamp descending and return latest N
        return sorted(filtered, key=lambda e: e.timestamp, reverse=True)[:limit]

    def get_high_confidence_evidence(
        self,
        min_confidence: float = 0.7,
        evidence_type: Optional[EvidenceType] = None,
    ) -> List[Evidence]:
        """Get evidence above confidence threshold."""
        filtered = self.evidence_store
        if evidence_type:
            filtered = [e for e in filtered if e.evidence_type == evidence_type]
        
        return [e for e in filtered if e.confidence >= min_confidence]

    def get_evidence_by_tags(self, tags: List[str]) -> List[Evidence]:
        """Get evidence that has any of the specified tags."""
        return [
            e for e in self.evidence_store
            if any(tag in e.tags for tag in tags)
        ]

    def clear_old_evidence(self, hours: int = 24) -> int:
        """Remove evidence older than N hours."""
        cutoff = datetime.now(timezone.utc)
        cutoff = cutoff - timedelta(hours=hours)
        
        initial_count = len(self.evidence_store)
        self.evidence_store = [
            e for e in self.evidence_store
            if e.timestamp > cutoff
        ]
        return initial_count - len(self.evidence_store)

    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get summary statistics of evidence."""
        return {
            "total_evidence": len(self.evidence_store),
            "by_type": {
                t.value: len([e for e in self.evidence_store if e.evidence_type == t])
                for t in EvidenceType
            },
            "average_confidence": (
                sum(e.confidence for e in self.evidence_store) / len(self.evidence_store)
                if self.evidence_store else 0.0
            ),
            "latest_timestamp": (
                max(e.timestamp for e in self.evidence_store).isoformat()
                if self.evidence_store else None
            ),
        }
