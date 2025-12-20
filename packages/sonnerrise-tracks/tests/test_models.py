"""Tests for Track models."""

from datetime import datetime, timedelta

from sonnerrise_core.config import Config, DatabaseConfig
from sonnerrise_core.database import get_database
from sonnerrise_core.models import import_all_models

from sonnerrise_tracks.models import Track, TrackEvent, TrackLink


class TestTrackModel:
    """Tests for Track SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert Track.__tablename__ == "tracks"

    def test_columns_exist(self):
        """Test that all expected columns exist."""
        columns = {c.name for c in Track.__table__.columns}
        expected = {
            "id", "title", "album", "definition_id",
            "cover_art_url", "lyrics", "comments",
            "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_repr(self):
        """Test string representation."""
        track = Track(title="Test Song")
        track.id = 42
        assert "Track" in repr(track)
        assert "42" in repr(track)
        assert "Test Song" in repr(track)

    def test_persistence(self):
        """Test persisting a track to database."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        import_all_models()
        db.create_tables()

        with db.session() as session:
            track = Track(
                title="Persistent Track",
                album="Test Album",
                lyrics="La la la",
            )
            session.add(track)
            session.commit()
            track_id = track.id

        with db.session() as session:
            loaded = session.query(Track).get(track_id)
            assert loaded is not None
            assert loaded.title == "Persistent Track"
            assert loaded.album == "Test Album"

        db.close()


class TestTrackEventModel:
    """Tests for TrackEvent SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert TrackEvent.__tablename__ == "track_events"

    def test_is_past(self):
        """Test is_past property."""
        event = TrackEvent(
            datetime=datetime.now() - timedelta(days=1),
            description="Past event",
        )
        assert event.is_past is True

        event = TrackEvent(
            datetime=datetime.now() + timedelta(days=1),
            description="Future event",
        )
        assert event.is_past is False

    def test_is_upcoming(self):
        """Test is_upcoming property."""
        # Future and enabled
        event = TrackEvent(
            datetime=datetime.now() + timedelta(days=1),
            description="Upcoming",
            enabled=True,
        )
        assert event.is_upcoming is True

        # Future but disabled
        event = TrackEvent(
            datetime=datetime.now() + timedelta(days=1),
            description="Disabled",
            enabled=False,
        )
        assert event.is_upcoming is False

        # Past
        event = TrackEvent(
            datetime=datetime.now() - timedelta(days=1),
            description="Past",
            enabled=True,
        )
        assert event.is_upcoming is False

    def test_persistence_with_track(self):
        """Test persisting events with track."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        import_all_models()
        db.create_tables()

        event_time = datetime.now() + timedelta(days=1)

        with db.session() as session:
            track = Track(title="Track with Events")
            session.add(track)
            session.flush()

            event = TrackEvent(
                track_id=track.id,
                datetime=event_time,
                description="Test event",
                enabled=True,
            )
            session.add(event)
            session.commit()
            track_id = track.id

        with db.session() as session:
            loaded = session.query(Track).get(track_id)
            assert len(loaded.events) == 1
            assert loaded.events[0].description == "Test event"

        db.close()


class TestTrackLinkModel:
    """Tests for TrackLink SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert TrackLink.__tablename__ == "track_links"

    def test_persistence_with_track(self):
        """Test persisting links with track."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        import_all_models()
        db.create_tables()

        with db.session() as session:
            track = Track(title="Track with Links")
            session.add(track)
            session.flush()

            link = TrackLink(
                track_id=track.id,
                url="https://example.com",
                description="Example link",
            )
            session.add(link)
            session.commit()
            track_id = track.id

        with db.session() as session:
            loaded = session.query(Track).get(track_id)
            assert len(loaded.links) == 1
            assert loaded.links[0].url == "https://example.com"

        db.close()
