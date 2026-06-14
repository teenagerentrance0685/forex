"""
Market Intelligence - Economic calendar and high-impact news monitoring.

Purpose:
- Detect major economic events
- Mark NO_TRADE periods during high-impact news
- Feed evidence to context manager
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum


class EventImpact(Enum):
    """Economic event impact level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCountry(Enum):
    """Countries with major forex impact."""

    US = "USD"
    EU = "EUR"
    GB = "GBP"
    JP = "JPY"
    CH = "CHF"
    CA = "CAD"
    AU = "AUD"
    NZ = "NZD"


@dataclass
class EconomicEvent:
    """Economic calendar event."""

    name: str
    country: EventCountry
    impact: EventImpact
    scheduled_time: datetime
    forecast: Optional[float] = None
    previous: Optional[float] = None
    actual: Optional[float] = None

    def is_upcoming(self, minutes_ahead: int = 60) -> bool:
        """Check if event is upcoming within N minutes."""
        now = datetime.now(timezone.utc)
        minutes_until = (self.scheduled_time - now).total_seconds() / 60
        return 0 < minutes_until < minutes_ahead


class EconomicCalendar:
    """
    Economic calendar manager.

    Tracks upcoming high-impact events and marks NO_TRADE windows.
    """

    def __init__(self):
        self.events: List[EconomicEvent] = []

    def add_event(self, event: EconomicEvent) -> None:
        """Add an economic event."""
        self.events.append(event)

    def get_upcoming_events(
        self,
        minutes_ahead: int = 60,
        impact_filter: Optional[EventImpact] = None,
    ) -> List[EconomicEvent]:
        """Get upcoming events."""
        upcoming = [e for e in self.events if e.is_upcoming(minutes_ahead)]

        if impact_filter:
            upcoming = [e for e in upcoming if e.impact == impact_filter]

        return sorted(upcoming, key=lambda e: e.scheduled_time)

    def should_block_trading(self, minutes_window: int = 30) -> bool:
        """
        Check if we should block trading due to upcoming high-impact events.

        Returns True if critical or multiple high-impact events are coming.
        """
        upcoming = self.get_upcoming_events(minutes_ahead=minutes_window)

        critical_events = [e for e in upcoming if e.impact == EventImpact.CRITICAL]
        high_impact_events = [e for e in upcoming if e.impact == EventImpact.HIGH]

        # Block if any critical event
        if critical_events:
            return True

        # Block if multiple high-impact events
        if len(high_impact_events) > 2:
            return True

        return False

    def get_event_summary(self) -> dict:
        """Get summary of upcoming events."""
        upcoming = self.get_upcoming_events(minutes_ahead=120)

        return {
            "upcoming_count": len(upcoming),
            "critical_count": sum(
                1 for e in upcoming if e.impact == EventImpact.CRITICAL
            ),
            "high_count": sum(1 for e in upcoming if e.impact == EventImpact.HIGH),
            "events": [
                {
                    "name": e.name,
                    "country": e.country.value,
                    "impact": e.impact.value,
                    "scheduled_time": e.scheduled_time.isoformat(),
                }
                for e in upcoming[:10]
            ],
        }
