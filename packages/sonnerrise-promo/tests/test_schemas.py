"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from sonnerrise_promo.schemas import (
    PromoCreate,
    PromoLinkCreate,
    PromoUpdate,
)


class TestPromoLinkCreate:
    """Tests for PromoLinkCreate schema."""

    def test_valid_link(self):
        """Test creating a valid link."""
        link = PromoLinkCreate(url="https://spotify.com/track/123", description="Spotify")
        assert link.url == "https://spotify.com/track/123"
        assert link.description == "Spotify"

    def test_url_required(self):
        """Test that URL is required."""
        with pytest.raises(ValidationError):
            PromoLinkCreate()

    def test_url_must_be_http(self):
        """Test that URL must start with http:// or https://."""
        with pytest.raises(ValidationError):
            PromoLinkCreate(url="ftp://example.com")

    def test_description_optional(self):
        """Test that description is optional."""
        link = PromoLinkCreate(url="https://example.com")
        assert link.description is None


class TestPromoCreate:
    """Tests for PromoCreate schema."""

    def test_valid_minimal(self):
        """Test creating with minimal fields."""
        promo = PromoCreate(track_id=1)
        assert promo.track_id == 1
        assert promo.track_art_definition is None
        assert promo.track_canvas_definition is None
        assert promo.pitch is None
        assert promo.links == []

    def test_valid_full(self):
        """Test creating with all fields."""
        promo = PromoCreate(
            track_id=1,
            track_art_definition="Epic fantasy landscape",
            track_canvas_definition="Slow zoom on art",
            pitch="Amazing new track!",
            links=[PromoLinkCreate(url="https://spotify.com")],
        )
        assert promo.track_id == 1
        assert promo.track_art_definition == "Epic fantasy landscape"
        assert len(promo.links) == 1

    def test_track_id_required(self):
        """Test that track_id is required."""
        with pytest.raises(ValidationError):
            PromoCreate()

    def test_text_stripped(self):
        """Test that text fields are stripped."""
        promo = PromoCreate(
            track_id=1,
            pitch="  Some pitch  ",
        )
        assert promo.pitch == "Some pitch"

    def test_empty_text_becomes_none(self):
        """Test that empty text becomes None."""
        promo = PromoCreate(
            track_id=1,
            pitch="   ",
        )
        assert promo.pitch is None


class TestPromoUpdate:
    """Tests for PromoUpdate schema."""

    def test_all_optional(self):
        """Test that all fields are optional."""
        update = PromoUpdate()
        assert update.track_art_definition is None
        assert update.pitch is None

    def test_partial_update(self):
        """Test updating only some fields."""
        update = PromoUpdate(pitch="New pitch")
        assert update.pitch == "New pitch"
        assert update.track_art_definition is None

    def test_model_dump_exclude_unset(self):
        """Test that unset fields are excluded."""
        update = PromoUpdate(pitch="New pitch")
        data = update.model_dump(exclude_unset=True)
        assert data == {"pitch": "New pitch"}
