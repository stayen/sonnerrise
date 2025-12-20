"""Tests for TrackRepository."""

from datetime import datetime, timedelta

import pytest

from sonnerrise_tracks import (
    EventCreate,
    EventUpdate,
    LinkCreate,
    TrackCreate,
    TrackFilter,
    TrackUpdate,
)
from sonnerrise_tracks.repository import EventNotFoundError, TrackNotFoundError


class TestTrackRepository:
    """Tests for TrackRepository."""

    def test_create_minimal(self, repo):
        """Test creating a track with minimal fields."""
        data = TrackCreate(title="Test Track")
        track = repo.create(data)

        assert track.id is not None
        assert track.title == "Test Track"
        assert track.album is None
        assert track.links == []
        assert track.events == []

    def test_create_with_links_and_events(self, repo):
        """Test creating a track with links and events."""
        event_time = datetime.now() + timedelta(days=1)
        data = TrackCreate(
            title="Full Track",
            album="Test Album",
            links=[
                LinkCreate(url="https://example.com/1", description="Link 1"),
            ],
            events=[
                EventCreate(datetime=event_time, description="Publish"),
            ],
        )
        track = repo.create(data)

        assert len(track.links) == 1
        assert track.links[0].url == "https://example.com/1"
        assert len(track.events) == 1
        assert track.events[0].description == "Publish"

    def test_get(self, repo):
        """Test getting a track by ID."""
        created = repo.create(TrackCreate(title="Get Test"))
        fetched = repo.get(created.id)

        assert fetched.id == created.id
        assert fetched.title == "Get Test"

    def test_get_not_found(self, repo):
        """Test getting non-existent track."""
        with pytest.raises(TrackNotFoundError) as exc_info:
            repo.get(9999)
        assert exc_info.value.track_id == 9999

    def test_get_or_none(self, repo):
        """Test get_or_none returns None for missing."""
        result = repo.get_or_none(9999)
        assert result is None

    def test_update(self, repo):
        """Test updating a track."""
        created = repo.create(TrackCreate(title="Original"))
        updated = repo.update(
            created.id,
            TrackUpdate(title="Updated", album="New Album"),
        )

        assert updated.id == created.id
        assert updated.title == "Updated"
        assert updated.album == "New Album"

    def test_update_links(self, repo):
        """Test updating track links."""
        created = repo.create(
            TrackCreate(
                title="Test",
                links=[LinkCreate(url="https://old.com")],
            )
        )
        updated = repo.update(
            created.id,
            TrackUpdate(links=[LinkCreate(url="https://new.com")]),
        )

        assert len(updated.links) == 1
        assert updated.links[0].url == "https://new.com"

    def test_delete(self, repo):
        """Test deleting a track."""
        created = repo.create(TrackCreate(title="Delete Me"))
        result = repo.delete(created.id)

        assert result is True
        assert repo.get_or_none(created.id) is None

    def test_delete_not_found(self, repo):
        """Test deleting non-existent track."""
        result = repo.delete(9999)
        assert result is False

    def test_list_empty(self, repo):
        """Test listing empty repository."""
        result = repo.list()

        assert result.items == []
        assert result.total == 0

    def test_list_with_items(self, repo):
        """Test listing with items."""
        for i in range(5):
            repo.create(TrackCreate(title=f"Track {i}"))

        result = repo.list()

        assert len(result.items) == 5
        assert result.total == 5

    def test_list_pagination(self, repo):
        """Test pagination."""
        for i in range(25):
            repo.create(TrackCreate(title=f"Track {i:02d}"))

        page1 = repo.list(page=1, per_page=10)
        page2 = repo.list(page=2, per_page=10)
        page3 = repo.list(page=3, per_page=10)

        assert len(page1.items) == 10
        assert len(page2.items) == 10
        assert len(page3.items) == 5
        assert page1.pages == 3

    def test_list_filter_by_title(self, repo):
        """Test filtering by title."""
        repo.create(TrackCreate(title="Alpha Song"))
        repo.create(TrackCreate(title="Beta Song"))
        repo.create(TrackCreate(title="Alpha Tune"))

        result = repo.list(filters=TrackFilter(title="Alpha"))

        assert len(result.items) == 2

    def test_list_filter_by_album(self, repo):
        """Test filtering by album."""
        repo.create(TrackCreate(title="Track 1", album="Album A"))
        repo.create(TrackCreate(title="Track 2", album="Album B"))
        repo.create(TrackCreate(title="Track 3", album="Album A"))

        result = repo.list(filters=TrackFilter(album="Album A"))

        assert len(result.items) == 2

    def test_search(self, repo):
        """Test searching tracks."""
        repo.create(TrackCreate(title="Epic Journey"))
        repo.create(TrackCreate(title="Soft Ballad"))
        repo.create(TrackCreate(title="Epic Battle"))

        results = repo.search("Epic")

        assert len(results) == 2

    def test_count(self, repo):
        """Test counting tracks."""
        assert repo.count() == 0

        for i in range(3):
            repo.create(TrackCreate(title=f"Track {i}"))

        assert repo.count() == 3

    def test_exists(self, repo):
        """Test checking if track exists."""
        assert repo.exists(9999) is False

        created = repo.create(TrackCreate(title="Exists"))
        assert repo.exists(created.id) is True


class TestTrackEventOperations:
    """Tests for track event operations."""

    def test_add_event(self, repo):
        """Test adding an event to a track."""
        created = repo.create(TrackCreate(title="Test"))
        event_time = datetime.now() + timedelta(days=1)
        updated = repo.add_event(
            created.id,
            EventCreate(datetime=event_time, description="Publish"),
        )

        assert len(updated.events) == 1
        assert updated.events[0].description == "Publish"

    def test_update_event(self, repo):
        """Test updating an event."""
        event_time = datetime.now() + timedelta(days=1)
        created = repo.create(
            TrackCreate(
                title="Test",
                events=[EventCreate(datetime=event_time, description="Old")],
            )
        )
        event_id = created.events[0].id

        updated = repo.update_event(
            created.id,
            event_id,
            EventUpdate(description="New"),
        )

        assert updated.events[0].description == "New"

    def test_remove_event(self, repo):
        """Test removing an event."""
        event_time = datetime.now() + timedelta(days=1)
        created = repo.create(
            TrackCreate(
                title="Test",
                events=[EventCreate(datetime=event_time, description="Remove")],
            )
        )
        event_id = created.events[0].id

        updated = repo.remove_event(created.id, event_id)

        assert len(updated.events) == 0

    def test_toggle_event(self, repo):
        """Test toggling event enabled status."""
        event_time = datetime.now() + timedelta(days=1)
        created = repo.create(
            TrackCreate(
                title="Test",
                events=[EventCreate(datetime=event_time, description="Toggle")],
            )
        )
        event_id = created.events[0].id
        assert created.events[0].enabled is True

        updated = repo.toggle_event(created.id, event_id)
        assert updated.events[0].enabled is False

        updated = repo.toggle_event(created.id, event_id)
        assert updated.events[0].enabled is True

    def test_get_upcoming_events(self, repo):
        """Test getting upcoming events."""
        # Create tracks with events
        future_time = datetime.now() + timedelta(days=3)
        past_time = datetime.now() - timedelta(days=1)
        far_future = datetime.now() + timedelta(days=30)

        repo.create(
            TrackCreate(
                title="Track 1",
                events=[EventCreate(datetime=future_time, description="Upcoming")],
            )
        )
        repo.create(
            TrackCreate(
                title="Track 2",
                events=[EventCreate(datetime=past_time, description="Past")],
            )
        )
        repo.create(
            TrackCreate(
                title="Track 3",
                events=[EventCreate(datetime=far_future, description="Far future")],
            )
        )

        upcoming = repo.get_upcoming_events(days=7)

        assert len(upcoming) == 1
        assert upcoming[0].description == "Upcoming"
        assert upcoming[0].track_title == "Track 1"

    def test_get_upcoming_events_excludes_disabled(self, repo):
        """Test that disabled events are excluded."""
        future_time = datetime.now() + timedelta(days=3)
        repo.create(
            TrackCreate(
                title="Test",
                events=[
                    EventCreate(
                        datetime=future_time,
                        description="Disabled",
                        enabled=False,
                    )
                ],
            )
        )

        upcoming = repo.get_upcoming_events(days=7)

        assert len(upcoming) == 0


class TestTrackLinkOperations:
    """Tests for track link operations."""

    def test_add_link(self, repo):
        """Test adding a link to a track."""
        created = repo.create(TrackCreate(title="Test"))
        updated = repo.add_link(created.id, "https://new-link.com", "New")

        assert len(updated.links) == 1
        assert updated.links[0].url == "https://new-link.com"

    def test_remove_link(self, repo):
        """Test removing a link from a track."""
        created = repo.create(
            TrackCreate(
                title="Test",
                links=[LinkCreate(url="https://remove.com")],
            )
        )
        link_id = created.links[0].id

        updated = repo.remove_link(created.id, link_id)

        assert len(updated.links) == 0
