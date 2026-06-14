"""
Economic Calendar Data Source - Track high-impact economic events.

Major economic indicators:
- Interest Rate Decisions
- Non-Farm Payroll (NFP)
- GDP Data
- Inflation (CPI/PPI)
- Employment Data
- Consumer Confidence
- PMI indices

Sources:
- Trading Economics API
- Forex Factory
- Investing.com
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum


class EventImportance(Enum):
    """Event importance level."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EconomicEvent:
    """Economic calendar event."""
    event_id: str
    event_name: str
    country: str  # USD, EUR, GBP, JPY, etc.
    importance: EventImportance
    scheduled_time: datetime
    
    # Event data
    forecast: Optional[float] = None
    previous: Optional[float] = None
    actual: Optional[float] = None
    
    # Impact details
    currency_pairs_affected: List[str] = None
    direction: Optional[str] = None  # up | down | sideways | unknown
    
    def is_upcoming(self, minutes_ahead: int = 120) -> bool:
        """Check if event is upcoming."""
        now = datetime.now(timezone.utc)
        minutes_until = (self.scheduled_time - now).total_seconds() / 60
        return 0 < minutes_until < minutes_ahead
    
    def is_released(self) -> bool:
        """Check if actual data is released."""
        return self.actual is not None
    
    def get_surprise(self) -> Optional[float]:
        """Get forecast vs actual surprise."""
        if self.actual is None or self.forecast is None:
            return None
        return self.actual - self.forecast


class EconomicCalendarReader:
    """
    Monitor economic calendar events.
    
    Note: Requires API integration with Trading Economics or similar.
    This is a template showing the interface.
    """

    # High-impact events
    HIGH_IMPACT_EVENTS = [
        "Interest Rate Decision",
        "Non-Farm Payroll",
        "GDP",
        "CPI",
        "NFP",
        "FOMC Meeting",
        "ECB Decision",
        "BOJ Decision",
    ]

    # Currency-impact mapping
    CURRENCY_MAPPING = {
        "USD": ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF"],
        "EUR": ["EURUSD", "EURGBP", "EURJPY", "EURCHF"],
        "GBP": ["GBPUSD", "GBPJPY", "EURGBP"],
        "JPY": ["USDJPY", "EURJPY", "GBPJPY"],
        "CAD": ["USDCAD", "CADCHF"],
        "CHF": ["USDCHF", "EURCHF", "CADCHF"],
    }

    def __init__(self):
        """Initialize calendar reader."""
        self.events: List[EconomicEvent] = []
        self._load_mock_events()

    def get_upcoming_events(
        self,
        hours_ahead: int = 24,
        importance_filter: Optional[EventImportance] = None,
    ) -> List[EconomicEvent]:
        """
        Get upcoming economic events.
        
        Args:
            hours_ahead: Look ahead N hours
            importance_filter: Filter by importance level
            
        Returns:
            Sorted list of upcoming events
        """
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=hours_ahead)
        
        upcoming = [
            e for e in self.events
            if now < e.scheduled_time <= cutoff
        ]
        
        if importance_filter:
            upcoming = [
                e for e in upcoming
                if e.importance == importance_filter
            ]
        
        return sorted(upcoming, key=lambda e: e.scheduled_time)

    def get_critical_events_window(self, minutes_window: int = 30) -> List[EconomicEvent]:
        """
        Get critical events within N minutes.
        
        Used for NO_TRADE_ENGINE to determine NO_TRADE windows.
        """
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(minutes=minutes_window)
        
        critical = [
            e for e in self.events
            if (now < e.scheduled_time <= cutoff and
                e.importance == EventImportance.CRITICAL)
        ]
        
        return sorted(critical, key=lambda e: e.scheduled_time)

    def get_high_impact_events_24h(self) -> List[EconomicEvent]:
        """Get all high-impact events in next 24 hours."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=24)
        
        high_impact = [
            e for e in self.events
            if (now < e.scheduled_time <= cutoff and
                e.importance in [EventImportance.HIGH, EventImportance.CRITICAL])
        ]
        
        return sorted(high_impact, key=lambda e: e.scheduled_time)

    def should_enter_no_trade_mode(self) -> tuple[bool, str]:
        """
        Determine if robot should enter NO_TRADE mode.
        
        Returns:
            (should_block, reason)
        """
        critical = self.get_critical_events_window(minutes_window=60)
        
        if critical:
            event_names = ", ".join(e.event_name for e in critical)
            return True, f"Critical events in next 60 min: {event_names}"
        
        high_impact = self.get_high_impact_events_24h()
        high_in_next_hour = [
            e for e in high_impact
            if (e.scheduled_time - datetime.now(timezone.utc)).total_seconds() < 3600
        ]
        
        if len(high_in_next_hour) > 2:
            event_names = ", ".join(e.event_name for e in high_in_next_hour)
            return True, f"Multiple high-impact events coming: {event_names}"
        
        return False, ""

    def get_affected_pairs(self, event: EconomicEvent) -> List[str]:
        """Get currency pairs affected by an event."""
        currency = event.country
        return self.CURRENCY_MAPPING.get(currency, [])

    def format_event_summary(self) -> Dict[str, Any]:
        """Format calendar summary for display."""
        upcoming_24h = self.get_high_impact_events_24h()
        
        return {
            "total_events_24h": len(upcoming_24h),
            "critical_events": len([e for e in upcoming_24h if e.importance == EventImportance.CRITICAL]),
            "high_impact_events": len([e for e in upcoming_24h if e.importance == EventImportance.HIGH]),
            "events": [
                {
                    "name": e.event_name,
                    "country": e.country,
                    "importance": e.importance.name,
                    "scheduled_time": e.scheduled_time.isoformat(),
                    "forecast": e.forecast,
                    "previous": e.previous,
                    "affected_pairs": self.get_affected_pairs(e),
                }
                for e in upcoming_24h
            ],
            "no_trade_active": self.should_enter_no_trade_mode()[0],
        }

    def _load_mock_events(self) -> None:
        """Load mock events for testing."""
        now = datetime.now(timezone.utc)
        
        self.events = [
            EconomicEvent(
                event_id="fed_1",
                event_name="Interest Rate Decision",
                country="USD",
                importance=EventImportance.CRITICAL,
                scheduled_time=now + timedelta(hours=2),
                forecast=5.50,
                previous=5.25,
                currency_pairs_affected=["EURUSD", "GBPUSD", "USDJPY"],
                direction="unknown",
            ),
            EconomicEvent(
                event_id="nfp_1",
                event_name="Non-Farm Payroll",
                country="USD",
                importance=EventImportance.CRITICAL,
                scheduled_time=now + timedelta(hours=6),
                forecast=180000,
                previous=175000,
                currency_pairs_affected=["EURUSD", "GBPUSD"],
                direction="up",
            ),
            EconomicEvent(
                event_id="ecb_1",
                event_name="ECB Interest Rate Decision",
                country="EUR",
                importance=EventImportance.HIGH,
                scheduled_time=now + timedelta(hours=12),
                forecast=4.75,
                previous=4.50,
                currency_pairs_affected=["EURUSD", "EURGBP"],
                direction="sideways",
            ),
            EconomicEvent(
                event_id="cpi_1",
                event_name="CPI (Year over Year)",
                country="USD",
                importance=EventImportance.HIGH,
                scheduled_time=now + timedelta(hours=18),
                forecast=3.2,
                previous=3.4,
                currency_pairs_affected=["EURUSD"],
                direction="down",
            ),
            EconomicEvent(
                event_id="pmi_1",
                event_name="PMI Manufacturing",
                country="USD",
                importance=EventImportance.MEDIUM,
                scheduled_time=now + timedelta(hours=24),
                forecast=50.5,
                previous=50.2,
                currency_pairs_affected=["EURUSD"],
                direction="unknown",
            ),
        ]


# Default instance
_calendar_reader: Optional[EconomicCalendarReader] = None


def get_calendar_reader() -> EconomicCalendarReader:
    """Get or create singleton calendar reader."""
    global _calendar_reader
    if _calendar_reader is None:
        _calendar_reader = EconomicCalendarReader()
    return _calendar_reader
