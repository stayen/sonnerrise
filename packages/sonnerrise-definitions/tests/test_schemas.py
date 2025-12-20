"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from sonnerrise_definitions.schemas import (
    DefinitionCreate,
    DefinitionUpdate,
    LinkCreate,
)
from sonnerrise_definitions.models import ModelVersion, PersonaType, VocalsType


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

    def test_description_optional(self):
        """Test that description is optional."""
        link = LinkCreate(url="https://example.com")
        assert link.description is None


class TestDefinitionCreate:
    """Tests for DefinitionCreate schema."""

    def test_valid_minimal_with_style(self):
        """Test creating with minimal fields using style."""
        definition = DefinitionCreate(
            title="Test Song",
            style_of_music="pop, upbeat",
        )
        assert definition.title == "Test Song"
        assert definition.style_of_music == "pop, upbeat"
        assert definition.model == ModelVersion.V4_0
        assert definition.vocals == VocalsType.ANY

    def test_valid_minimal_with_lyrics(self):
        """Test creating with minimal fields using lyrics."""
        definition = DefinitionCreate(
            title="Test Song",
            lyrics="La la la...",
        )
        assert definition.lyrics == "La la la..."

    def test_valid_full(self):
        """Test creating with all fields."""
        definition = DefinitionCreate(
            title="Full Song",
            annotation="A test song",
            model=ModelVersion.V4_5_PLUS,
            style_of_music="epic orchestral",
            lyrics="[Verse]\nHello world",
            persona_id=1,
            persona_type=PersonaType.VOICE,
            vocals=VocalsType.FEMALE,
            audio_influence=30,
            style_influence=60,
            weirdness=40,
            comments="Test comment",
            links=[LinkCreate(url="https://example.com")],
        )
        assert definition.title == "Full Song"
        assert definition.model == ModelVersion.V4_5_PLUS
        assert len(definition.links) == 1

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            DefinitionCreate(style_of_music="pop")

    def test_title_not_empty(self):
        """Test that title cannot be empty."""
        with pytest.raises(ValidationError):
            DefinitionCreate(title="", style_of_music="pop")

    def test_title_not_whitespace(self):
        """Test that title cannot be only whitespace."""
        with pytest.raises(ValidationError):
            DefinitionCreate(title="   ", style_of_music="pop")

    def test_style_or_lyrics_required(self):
        """Test that either style or lyrics must be provided."""
        with pytest.raises(ValidationError):
            DefinitionCreate(title="Test")

    def test_persona_type_required_with_persona(self):
        """Test that persona_type is required when persona_id is set."""
        with pytest.raises(ValidationError):
            DefinitionCreate(
                title="Test",
                style_of_music="pop",
                persona_id=1,
            )

    def test_older_models_style_length(self):
        """Test style length validation with older_models_style."""
        with pytest.raises(ValidationError):
            DefinitionCreate(
                title="Test",
                style_of_music="x" * 201,
                older_models_style=True,
            )

    def test_influence_range(self):
        """Test influence values must be 0-100."""
        with pytest.raises(ValidationError):
            DefinitionCreate(
                title="Test",
                style_of_music="pop",
                audio_influence=101,
            )

        with pytest.raises(ValidationError):
            DefinitionCreate(
                title="Test",
                style_of_music="pop",
                audio_influence=-1,
            )


class TestDefinitionUpdate:
    """Tests for DefinitionUpdate schema."""

    def test_all_optional(self):
        """Test that all fields are optional."""
        update = DefinitionUpdate()
        assert update.title is None
        assert update.model is None

    def test_partial_update(self):
        """Test updating only some fields."""
        update = DefinitionUpdate(title="New Title", model=ModelVersion.V5_0)
        assert update.title == "New Title"
        assert update.model == ModelVersion.V5_0
        assert update.style_of_music is None

    def test_model_dump_exclude_unset(self):
        """Test that unset fields are excluded."""
        update = DefinitionUpdate(title="New Title")
        data = update.model_dump(exclude_unset=True)
        assert data == {"title": "New Title"}
