"""Tests for PromoRepository."""

import pytest

from sonnerrise_promo import (
    PromoCreate,
    PromoFilter,
    PromoLinkCreate,
    PromoUpdate,
)
from sonnerrise_promo.repository import PromoExistsError, PromoNotFoundError


class TestPromoRepository:
    """Tests for PromoRepository."""

    def test_create_minimal(self, repo, track):
        """Test creating a promo with minimal fields."""
        data = PromoCreate(track_id=track)
        promo = repo.create(data)

        assert promo.id is not None
        assert promo.track_id == track
        assert promo.track_art_definition is None
        assert promo.pitch is None
        assert promo.links == []

    def test_create_full(self, repo, track):
        """Test creating a promo with all fields."""
        data = PromoCreate(
            track_id=track,
            track_art_definition="Epic art",
            track_canvas_definition="Video prompt",
            pitch="Amazing track!",
            links=[PromoLinkCreate(url="https://spotify.com", description="Spotify")],
        )
        promo = repo.create(data)

        assert promo.track_art_definition == "Epic art"
        assert promo.track_canvas_definition == "Video prompt"
        assert promo.pitch == "Amazing track!"
        assert len(promo.links) == 1

    def test_create_duplicate_fails(self, repo, track):
        """Test that creating duplicate promo for track fails."""
        repo.create(PromoCreate(track_id=track))

        with pytest.raises(PromoExistsError) as exc_info:
            repo.create(PromoCreate(track_id=track))
        assert exc_info.value.track_id == track

    def test_get(self, repo, track):
        """Test getting a promo by ID."""
        created = repo.create(PromoCreate(track_id=track, pitch="Test"))
        fetched = repo.get(created.id)

        assert fetched.id == created.id
        assert fetched.pitch == "Test"

    def test_get_not_found(self, repo):
        """Test getting non-existent promo."""
        with pytest.raises(PromoNotFoundError) as exc_info:
            repo.get(9999)
        assert exc_info.value.promo_id == 9999

    def test_get_or_none(self, repo):
        """Test get_or_none returns None for missing."""
        result = repo.get_or_none(9999)
        assert result is None

    def test_get_by_track(self, repo, track):
        """Test getting promo by track ID."""
        repo.create(PromoCreate(track_id=track, pitch="Track promo"))
        promo = repo.get_by_track(track)

        assert promo is not None
        assert promo.track_id == track
        assert promo.pitch == "Track promo"

    def test_get_by_track_not_found(self, repo):
        """Test get_by_track returns None for missing."""
        result = repo.get_by_track(9999)
        assert result is None

    def test_update(self, repo, track):
        """Test updating a promo."""
        created = repo.create(PromoCreate(track_id=track, pitch="Original"))
        updated = repo.update(created.id, PromoUpdate(pitch="Updated"))

        assert updated.id == created.id
        assert updated.pitch == "Updated"

    def test_update_links(self, repo, track):
        """Test updating promo links."""
        created = repo.create(
            PromoCreate(
                track_id=track,
                links=[PromoLinkCreate(url="https://old.com")],
            )
        )
        updated = repo.update(
            created.id,
            PromoUpdate(links=[PromoLinkCreate(url="https://new.com")]),
        )

        assert len(updated.links) == 1
        assert updated.links[0].url == "https://new.com"

    def test_delete(self, repo, track):
        """Test deleting a promo."""
        created = repo.create(PromoCreate(track_id=track))
        result = repo.delete(created.id)

        assert result is True
        assert repo.get_or_none(created.id) is None

    def test_delete_not_found(self, repo):
        """Test deleting non-existent promo."""
        result = repo.delete(9999)
        assert result is False

    def test_delete_by_track(self, repo, track):
        """Test deleting promo by track ID."""
        repo.create(PromoCreate(track_id=track))
        result = repo.delete_by_track(track)

        assert result is True
        assert repo.get_by_track(track) is None

    def test_list_empty(self, repo):
        """Test listing empty repository."""
        result = repo.list()

        assert result.items == []
        assert result.total == 0

    def test_list_with_items(self, repo, db):
        """Test listing with items."""
        # Create multiple tracks and promos
        from sonnerrise_tracks.models import Track

        with db.session() as session:
            for i in range(5):
                track = Track(title=f"Track {i}")
                session.add(track)
            session.commit()

        for i in range(1, 6):
            repo.create(PromoCreate(track_id=i))

        result = repo.list()

        assert len(result.items) == 5
        assert result.total == 5

    def test_list_filter_has_pitch(self, repo, db):
        """Test filtering by has_pitch."""
        from sonnerrise_tracks.models import Track

        with db.session() as session:
            for i in range(3):
                track = Track(title=f"Track {i}")
                session.add(track)
            session.commit()

        repo.create(PromoCreate(track_id=1, pitch="Has pitch"))
        repo.create(PromoCreate(track_id=2))
        repo.create(PromoCreate(track_id=3, pitch="Also has pitch"))

        result = repo.list(filters=PromoFilter(has_pitch=True))
        assert len(result.items) == 2

        result = repo.list(filters=PromoFilter(has_pitch=False))
        assert len(result.items) == 1

    def test_count(self, repo, track):
        """Test counting promos."""
        assert repo.count() == 0

        repo.create(PromoCreate(track_id=track))
        assert repo.count() == 1

    def test_exists(self, repo, track):
        """Test checking if promo exists."""
        assert repo.exists(9999) is False

        created = repo.create(PromoCreate(track_id=track))
        assert repo.exists(created.id) is True

    def test_exists_for_track(self, repo, track):
        """Test checking if promo exists for track."""
        assert repo.exists_for_track(track) is False

        repo.create(PromoCreate(track_id=track))
        assert repo.exists_for_track(track) is True

    def test_get_or_create_for_track_creates(self, repo, track):
        """Test get_or_create_for_track creates new promo."""
        promo = repo.get_or_create_for_track(track)

        assert promo is not None
        assert promo.track_id == track

    def test_get_or_create_for_track_gets_existing(self, repo, track):
        """Test get_or_create_for_track returns existing promo."""
        created = repo.create(PromoCreate(track_id=track, pitch="Original"))
        fetched = repo.get_or_create_for_track(track)

        assert fetched.id == created.id
        assert fetched.pitch == "Original"


class TestPromoLinkOperations:
    """Tests for promo link operations."""

    def test_add_link(self, repo, track):
        """Test adding a link to a promo."""
        created = repo.create(PromoCreate(track_id=track))
        updated = repo.add_link(created.id, "https://new-link.com", "New")

        assert len(updated.links) == 1
        assert updated.links[0].url == "https://new-link.com"

    def test_remove_link(self, repo, track):
        """Test removing a link from a promo."""
        created = repo.create(
            PromoCreate(
                track_id=track,
                links=[PromoLinkCreate(url="https://remove.com")],
            )
        )
        link_id = created.links[0].id

        updated = repo.remove_link(created.id, link_id)

        assert len(updated.links) == 0
