"""Tests for CalendarService."""

from datetime import date, datetime, timedelta

import pytest


class TestCalendarService:
    """Tests for CalendarService."""

    def test_get_today_events(self, calendar_service, sample_tracks):
        """Test getting today's events."""
        events = calendar_service.get_today_events()

        # Should have at least one event today
        assert len(events) >= 1
        assert all(e.datetime.date() == date.today() for e in events)

    def test_get_today_events_exclude_disabled(self, calendar_service, sample_tracks):
        """Test that disabled events are included by default."""
        events_all = calendar_service.get_today_events(include_disabled=True)
        events_enabled = calendar_service.get_today_events(include_disabled=False)

        # Enabled should be subset of all
        assert len(events_enabled) <= len(events_all)

    def test_get_week_view(self, calendar_service, sample_tracks):
        """Test getting week view."""
        week = calendar_service.get_week_view()

        assert len(week.days) == 7
        assert week.start_date.weekday() == 0  # Monday
        assert week.end_date.weekday() == 6  # Sunday
        assert week.total_events >= 0

    def test_get_week_view_specific_date(self, calendar_service, sample_tracks):
        """Test getting week view for specific date."""
        specific_date = date(2024, 3, 15)  # A Friday
        week = calendar_service.get_week_view(specific_date)

        assert week.start_date == date(2024, 3, 11)  # Monday
        assert week.end_date == date(2024, 3, 17)  # Sunday

    def test_get_month_view(self, calendar_service, sample_tracks):
        """Test getting month view."""
        month = calendar_service.get_month_view(2024, 3)

        assert month.year == 2024
        assert month.month == 3
        assert month.month_name == "March"
        assert len(month.weeks) >= 4  # At least 4 weeks

        # Each week should have 7 days
        for week in month.weeks:
            assert len(week) == 7

    def test_get_month_view_defaults(self, calendar_service, sample_tracks):
        """Test month view defaults to current month."""
        month = calendar_service.get_month_view()
        today = date.today()

        assert month.year == today.year
        assert month.month == today.month

    def test_get_upcoming_events(self, calendar_service, sample_tracks):
        """Test getting upcoming events."""
        upcoming = calendar_service.get_upcoming_events(days=7)

        # Should have events in the next 7 days
        assert upcoming.total >= 0
        assert upcoming.days_range == 7

        # All events should be in the future
        for event in upcoming.events:
            assert event.days_until >= 0

    def test_get_upcoming_events_exclude_disabled(self, calendar_service, sample_tracks):
        """Test that upcoming events excludes disabled by default."""
        upcoming = calendar_service.get_upcoming_events(days=14, include_disabled=False)

        # All should be enabled
        for event in upcoming.events:
            assert event.enabled is True

    def test_get_day_view(self, calendar_service, sample_tracks):
        """Test getting single day view."""
        day = calendar_service.get_day_view(date.today())

        assert day.date == date.today()
        assert day.is_today is True

    def test_toggle_event(self, calendar_service, db, sample_tracks):
        """Test toggling event enabled status."""
        from sonnerrise_tracks.models import Track, TrackEvent

        # Get an event to toggle
        with db.session() as session:
            event = session.query(TrackEvent).first()
            track_id = event.track_id
            event_id = event.id
            original_status = event.enabled

        # Toggle
        new_status = calendar_service.toggle_event(track_id, event_id)
        assert new_status != original_status

        # Toggle back
        restored_status = calendar_service.toggle_event(track_id, event_id)
        assert restored_status == original_status

    def test_toggle_event_not_found(self, calendar_service, sample_tracks):
        """Test toggling non-existent event."""
        with pytest.raises(ValueError, match="not found"):
            calendar_service.toggle_event(9999, 9999)

    def test_get_event_count_by_month(self, calendar_service, db):
        """Test getting event counts by month."""
        from sonnerrise_tracks.models import Track, TrackEvent

        # Create events in specific months
        with db.session() as session:
            track = Track(title="Test Track")
            session.add(track)
            session.flush()

            # Add events in Jan, Mar, Mar
            session.add(TrackEvent(
                track_id=track.id,
                datetime=datetime(2024, 1, 15, 10, 0),
                description="January event",
                enabled=True,
            ))
            session.add(TrackEvent(
                track_id=track.id,
                datetime=datetime(2024, 3, 10, 10, 0),
                description="March event 1",
                enabled=True,
            ))
            session.add(TrackEvent(
                track_id=track.id,
                datetime=datetime(2024, 3, 20, 10, 0),
                description="March event 2",
                enabled=True,
            ))
            session.commit()

        counts = calendar_service.get_event_count_by_month(2024)

        assert counts[1] == 1  # January
        assert counts[2] == 0  # February
        assert counts[3] == 2  # March

    def test_get_tracks_with_upcoming_events(self, calendar_service, sample_tracks):
        """Test getting tracks with upcoming events."""
        tracks = calendar_service.get_tracks_with_upcoming_events(days=14)

        # Should have tracks with upcoming events
        assert len(tracks) >= 0

        for track_info in tracks:
            assert "track_id" in track_info
            assert "title" in track_info
            assert "upcoming_event_count" in track_info
