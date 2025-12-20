"""Tests for calendar schemas."""

from datetime import date, datetime, timedelta

from sonnerrise_calendar.schemas import (
    CalendarDay,
    CalendarEvent,
    EventList,
    MonthView,
    UpcomingEvent,
    WeekView,
)


class TestCalendarEvent:
    """Tests for CalendarEvent schema."""

    def test_days_until_future(self):
        """Test days_until for future event."""
        future = datetime.now() + timedelta(days=5)
        event = CalendarEvent(
            event_id=1,
            track_id=1,
            track_title="Test",
            datetime=future,
            description="Future event",
            enabled=True,
        )
        assert event.days_until >= 4  # Could be 4 or 5 depending on time

    def test_days_until_past(self):
        """Test days_until for past event."""
        past = datetime.now() - timedelta(days=3)
        event = CalendarEvent(
            event_id=1,
            track_id=1,
            track_title="Test",
            datetime=past,
            description="Past event",
            enabled=True,
        )
        assert event.days_until < 0

    def test_is_past(self):
        """Test is_past property."""
        past = datetime.now() - timedelta(hours=1)
        event = CalendarEvent(
            event_id=1,
            track_id=1,
            track_title="Test",
            datetime=past,
            description="Past",
            enabled=True,
        )
        assert event.is_past is True

    def test_is_today(self):
        """Test is_today property."""
        today = datetime.now() + timedelta(hours=1)
        event = CalendarEvent(
            event_id=1,
            track_id=1,
            track_title="Test",
            datetime=today,
            description="Today",
            enabled=True,
        )
        assert event.is_today is True

    def test_time_str(self):
        """Test time_str formatting."""
        dt = datetime(2024, 3, 15, 14, 30)
        event = CalendarEvent(
            event_id=1,
            track_id=1,
            track_title="Test",
            datetime=dt,
            description="Test",
            enabled=True,
        )
        assert event.time_str == "14:30"


class TestCalendarDay:
    """Tests for CalendarDay schema."""

    def test_is_today(self):
        """Test is_today property."""
        day = CalendarDay(date=date.today())
        assert day.is_today is True

    def test_is_past(self):
        """Test is_past property."""
        yesterday = date.today() - timedelta(days=1)
        day = CalendarDay(date=yesterday)
        assert day.is_past is True

    def test_event_count(self):
        """Test event_count property."""
        events = [
            CalendarEvent(
                event_id=i,
                track_id=1,
                track_title="Test",
                datetime=datetime.now(),
                description=f"Event {i}",
                enabled=True,
            )
            for i in range(3)
        ]
        day = CalendarDay(date=date.today(), events=events)
        assert day.event_count == 3

    def test_enabled_event_count(self):
        """Test enabled_event_count property."""
        events = [
            CalendarEvent(
                event_id=1, track_id=1, track_title="Test",
                datetime=datetime.now(), description="Enabled", enabled=True,
            ),
            CalendarEvent(
                event_id=2, track_id=1, track_title="Test",
                datetime=datetime.now(), description="Disabled", enabled=False,
            ),
        ]
        day = CalendarDay(date=date.today(), events=events)
        assert day.enabled_event_count == 1


class TestWeekView:
    """Tests for WeekView schema."""

    def test_total_events(self):
        """Test total_events property."""
        days = [
            CalendarDay(
                date=date.today() + timedelta(days=i),
                events=[
                    CalendarEvent(
                        event_id=i, track_id=1, track_title="Test",
                        datetime=datetime.now(), description="Event", enabled=True,
                    )
                ] if i % 2 == 0 else []
            )
            for i in range(7)
        ]
        week = WeekView(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=6),
            days=days,
        )
        assert week.total_events == 4  # Days 0, 2, 4, 6


class TestUpcomingEvent:
    """Tests for UpcomingEvent schema."""

    def test_urgency_now(self):
        """Test urgency for today's event."""
        event = UpcomingEvent(
            event_id=1, track_id=1, track_title="Test", track_album=None,
            datetime=datetime.now(), description="Now", enabled=True,
            days_until=0,
        )
        assert event.urgency == "now"

    def test_urgency_tomorrow(self):
        """Test urgency for tomorrow's event."""
        event = UpcomingEvent(
            event_id=1, track_id=1, track_title="Test", track_album=None,
            datetime=datetime.now() + timedelta(days=1), description="Tomorrow",
            enabled=True, days_until=1,
        )
        assert event.urgency == "tomorrow"

    def test_urgency_soon(self):
        """Test urgency for event in 2-3 days."""
        event = UpcomingEvent(
            event_id=1, track_id=1, track_title="Test", track_album=None,
            datetime=datetime.now() + timedelta(days=2), description="Soon",
            enabled=True, days_until=2,
        )
        assert event.urgency == "soon"

    def test_urgency_this_week(self):
        """Test urgency for event in 4-7 days."""
        event = UpcomingEvent(
            event_id=1, track_id=1, track_title="Test", track_album=None,
            datetime=datetime.now() + timedelta(days=5), description="This week",
            enabled=True, days_until=5,
        )
        assert event.urgency == "this_week"

    def test_urgency_later(self):
        """Test urgency for event more than a week away."""
        event = UpcomingEvent(
            event_id=1, track_id=1, track_title="Test", track_album=None,
            datetime=datetime.now() + timedelta(days=10), description="Later",
            enabled=True, days_until=10,
        )
        assert event.urgency == "later"


class TestEventList:
    """Tests for EventList schema."""

    def test_has_urgent_true(self):
        """Test has_urgent when there are urgent events."""
        events = [
            UpcomingEvent(
                event_id=1, track_id=1, track_title="Test", track_album=None,
                datetime=datetime.now(), description="Today", enabled=True,
                days_until=0,
            ),
        ]
        event_list = EventList(events=events, total=1)
        assert event_list.has_urgent is True

    def test_has_urgent_false(self):
        """Test has_urgent when no urgent events."""
        events = [
            UpcomingEvent(
                event_id=1, track_id=1, track_title="Test", track_album=None,
                datetime=datetime.now() + timedelta(days=5), description="Later",
                enabled=True, days_until=5,
            ),
        ]
        event_list = EventList(events=events, total=1)
        assert event_list.has_urgent is False

    def test_by_urgency(self):
        """Test by_urgency grouping."""
        events = [
            UpcomingEvent(
                event_id=1, track_id=1, track_title="Test", track_album=None,
                datetime=datetime.now(), description="Today", enabled=True,
                days_until=0,
            ),
            UpcomingEvent(
                event_id=2, track_id=1, track_title="Test", track_album=None,
                datetime=datetime.now() + timedelta(days=5), description="Later",
                enabled=True, days_until=5,
            ),
        ]
        event_list = EventList(events=events, total=2)
        grouped = event_list.by_urgency
        assert len(grouped["now"]) == 1
        assert len(grouped["this_week"]) == 1
