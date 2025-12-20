"""Pytest configuration and fixtures for sonnerrise-calendar tests."""

from datetime import datetime, timedelta

import pytest

from sonnerrise_core.config import Config, DatabaseConfig
from sonnerrise_core.database import get_database
from sonnerrise_core.models import import_all_models


@pytest.fixture
def db():
    """Create a test database with SQLite in-memory."""
    config = Config(
        database=DatabaseConfig(
            plugin="sqlite",
            database=":memory:",
        )
    )
    database = get_database(config)
    import_all_models()
    database.create_tables()
    yield database
    database.close()


@pytest.fixture
def calendar_service(db):
    """Create a CalendarService with test database."""
    from sonnerrise_calendar import CalendarService

    return CalendarService(db)


@pytest.fixture
def sample_tracks(db):
    """Create sample tracks with events."""
    from sonnerrise_tracks.models import Track, TrackEvent

    now = datetime.now()

    with db.session() as session:
        # Track 1 with events today and tomorrow
        track1 = Track(title="Track One", album="Album A")
        session.add(track1)
        session.flush()

        session.add(TrackEvent(
            track_id=track1.id,
            datetime=now + timedelta(hours=2),
            description="Event today",
            enabled=True,
        ))
        session.add(TrackEvent(
            track_id=track1.id,
            datetime=now + timedelta(days=1, hours=3),
            description="Event tomorrow",
            enabled=True,
        ))

        # Track 2 with events next week
        track2 = Track(title="Track Two", album="Album B")
        session.add(track2)
        session.flush()

        session.add(TrackEvent(
            track_id=track2.id,
            datetime=now + timedelta(days=5),
            description="Event next week",
            enabled=True,
        ))
        session.add(TrackEvent(
            track_id=track2.id,
            datetime=now + timedelta(days=10),
            description="Event disabled",
            enabled=False,
        ))

        session.commit()

        return [track1.id, track2.id]
