"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from sonnerrise_personas.schemas import PersonaCreate, PersonaUpdate


class TestPersonaCreate:
    """Tests for PersonaCreate schema."""

    def test_valid_minimal(self):
        """Test creating with minimal required fields."""
        persona = PersonaCreate(name="Test Persona")
        assert persona.name == "Test Persona"
        assert persona.style_of_music is None
        assert persona.parental_track_id is None
        assert persona.comments is None

    def test_valid_full(self):
        """Test creating with all fields."""
        persona = PersonaCreate(
            name="Full Persona",
            style_of_music="epic orchestral",
            parental_track_id=42,
            comments="Some notes",
        )
        assert persona.name == "Full Persona"
        assert persona.style_of_music == "epic orchestral"
        assert persona.parental_track_id == 42
        assert persona.comments == "Some notes"

    def test_name_trimmed(self):
        """Test that name is trimmed."""
        persona = PersonaCreate(name="  Test  ")
        assert persona.name == "Test"

    def test_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            PersonaCreate()

    def test_name_not_empty(self):
        """Test that name cannot be empty."""
        with pytest.raises(ValidationError):
            PersonaCreate(name="")

    def test_name_not_whitespace(self):
        """Test that name cannot be only whitespace."""
        with pytest.raises(ValidationError):
            PersonaCreate(name="   ")

    def test_name_max_length(self):
        """Test name maximum length."""
        with pytest.raises(ValidationError):
            PersonaCreate(name="x" * 49)

    def test_style_max_length(self):
        """Test style_of_music maximum length."""
        with pytest.raises(ValidationError):
            PersonaCreate(name="Test", style_of_music="x" * 1001)

    def test_style_trimmed(self):
        """Test that style is trimmed."""
        persona = PersonaCreate(name="Test", style_of_music="  epic  ")
        assert persona.style_of_music == "epic"

    def test_style_empty_becomes_none(self):
        """Test that empty style becomes None."""
        persona = PersonaCreate(name="Test", style_of_music="   ")
        assert persona.style_of_music is None


class TestPersonaUpdate:
    """Tests for PersonaUpdate schema."""

    def test_all_optional(self):
        """Test that all fields are optional."""
        update = PersonaUpdate()
        assert update.name is None
        assert update.style_of_music is None

    def test_partial_update(self):
        """Test updating only some fields."""
        update = PersonaUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.style_of_music is None

    def test_name_validation(self):
        """Test that name validation still applies."""
        with pytest.raises(ValidationError):
            PersonaUpdate(name="")

    def test_model_dump_exclude_unset(self):
        """Test that unset fields are excluded."""
        update = PersonaUpdate(name="New Name")
        data = update.model_dump(exclude_unset=True)
        assert data == {"name": "New Name"}
