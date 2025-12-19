"""Tests for Pydantic schemas."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from sonnerrise_tracks.schemas import (
    EventCreate,
    EventUpdate,
    LinkCreate,
    TrackCreate,
    TrackUpdate,
)


class TestLinkCreate:
    """Tests for LinkCreate schema."""

    def test_valid_link(self):
        """Test creating a valid link."""
        link = LinkCreate(url="https://example.com", description="Example")
        assert link.url == "https://example.com"
        assert link.description == "Example"

    def test_url_required(self):
        """Test that URL is required."""
        with pytest.raises(ValidationError):
            LinkCreate()

    def test_url_must_be_http(self):
        """Test that URL must start with http:// or https://."""
        with pytest.raises(ValidationError):
            LinkCreate(url="ftp://example.com")


class TestEventCreate:
    """Tests for EventCreate schema."""

    def test_valid_event(self):
        """Test creating a valid event."""
        event_time = datetime.now() + timedelta(days=1)
        event = EventCreate(
            datetime=event_time,
            description="Publish to Spotify",
        )
        assert event.datetime == event_time
        assert event.description == "Publish to Spotify"
        assert event.enabled is True

    def test_datetime_required(self):
        """Test that datetime is required."""
        with pytest.raises(ValidationError):
            EventCreate(description="Test")

    def test_description_required(self):
        """Test that description is required."""
        with pytest.raises(ValidationError):
            EventCreate(datetime=datetime.now())

    def test_description_not_empty(self):
        """Test that description cannot be empty."""
        with pytest.raises(ValidationError):
            EventCreate(datetime=datetime.now(), description="")

    def test_description_trimmed(self):
        """Test that description is trimmed."""
        event = EventCreate(
            datetime=datetime.now(),
            description="  Publish  ",
        )
        assert event.description == "Publish"

    def test_enabled_default(self):
        """Test that enabled defaults to True."""
        event = EventCreate(
            datetime=datetime.now(),
            description="Test",
        )
        assert event.enabled is True


class TestEventUpdate:
    """Tests for EventUpdate schema."""

    def test_all_optional(self):
        """Test that all fields are optional."""
        update = EventUpdate()
        assert update.datetime is None
        assert update.description is None
        assert update.enabled is None

    def test_partial_update(self):
        """Test updating only some fields."""
        update = EventUpdate(enabled=False)
        assert update.enabled is False
        assert update.datetime is None


class TestTrackCreate:
    """Tests for TrackCreate schema."""

    def test_valid_minimal(self):
        """Test creating with minimal fields."""
        track = TrackCreate(title="Test Track")
        assert track.title == "Test Track"
        assert track.album is None
        assert track.links == []
        assert track.events == []

    def test_valid_full(self):
        """Test creating with all fields."""
        event_time = datetime.now() + timedelta(days=1)
        track = TrackCreate(
            title="Full Track",
            album="Test Album",
            definition_id=1,
            cover_art_url="https://example.com/cover.jpg",
            lyrics="La la la",
            comments="Test comment",
            links=[LinkCreate(url="https://example.com")],
            events=[EventCreate(datetime=event_time, description="Publish")],
        )
        assert track.title == "Full Track"
        assert track.album == "Test Album"
        assert len(track.links) == 1
        assert len(track.events) == 1

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            TrackCreate()

    def test_title_not_empty(self):
        """Test that title cannot be empty."""
        with pytest.raises(ValidationError):
            TrackCreate(title="")

    def test_title_trimmed(self):
        """Test that title is trimmed."""
        track = TrackCreate(title="  Test  ")
        assert track.title == "Test"

    def test_cover_art_url_validation(self):
        """Test cover art URL validation."""
        with pytest.raises(ValidationError):
            TrackCreate(title="Test", cover_art_url="not-a-url")


class TestTrackUpdate:
    """Tests for TrackUpdate schema."""

    def test_all_optional(self):
        """Test that all fields are optional."""
        update = TrackUpdate()
        assert update.title is None

    def test_partial_update(self):
        """Test updating only some fields."""
        update = TrackUpdate(title="New Title", album="New Album")
        assert update.title == "New Title"
        assert update.album == "New Album"
        assert update.lyrics is None

    def test_model_dump_exclude_unset(self):
        """Test that unset fields are excluded."""
        update = TrackUpdate(title="New Title")
        data = update.model_dump(exclude_unset=True)
        assert data == {"title": "New Title"}
