"""Tests for Promo models."""

from sonnerrise_core.config import Config, DatabaseConfig
from sonnerrise_core.database import get_database

from sonnerrise_promo.models import Promo, PromoLink


class TestPromoModel:
    """Tests for Promo SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert Promo.__tablename__ == "promos"

    def test_columns_exist(self):
        """Test that all expected columns exist."""
        columns = {c.name for c in Promo.__table__.columns}
        expected = {
            "id", "track_id",
            "track_art_definition", "track_canvas_definition",
            "pitch", "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_repr(self):
        """Test string representation."""
        promo = Promo(track_id=42)
        promo.id = 1
        assert "Promo" in repr(promo)
        assert "1" in repr(promo)
        assert "42" in repr(promo)

    def test_persistence(self):
        """Test persisting a promo to database."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        db.create_tables()

        # Create a track first
        from sonnerrise_tracks.models import Track

        with db.session() as session:
            track = Track(title="Test Track")
            session.add(track)
            session.commit()
            track_id = track.id

        with db.session() as session:
            promo = Promo(
                track_id=track_id,
                track_art_definition="Fantasy landscape",
                pitch="Amazing track!",
            )
            session.add(promo)
            session.commit()
            promo_id = promo.id

        with db.session() as session:
            loaded = session.query(Promo).get(promo_id)
            assert loaded is not None
            assert loaded.track_id == track_id
            assert loaded.track_art_definition == "Fantasy landscape"
            assert loaded.pitch == "Amazing track!"

        db.close()


class TestPromoLinkModel:
    """Tests for PromoLink SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert PromoLink.__tablename__ == "promo_links"

    def test_persistence_with_promo(self):
        """Test persisting links with promo."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        db.create_tables()

        # Create a track first
        from sonnerrise_tracks.models import Track

        with db.session() as session:
            track = Track(title="Test Track")
            session.add(track)
            session.commit()
            track_id = track.id

        with db.session() as session:
            promo = Promo(track_id=track_id)
            session.add(promo)
            session.flush()

            link = PromoLink(
                promo_id=promo.id,
                url="https://spotify.com/track/123",
                description="Spotify",
            )
            session.add(link)
            session.commit()
            promo_id = promo.id

        with db.session() as session:
            loaded = session.query(Promo).get(promo_id)
            assert len(loaded.links) == 1
            assert loaded.links[0].url == "https://spotify.com/track/123"
            assert loaded.links[0].description == "Spotify"

        db.close()
