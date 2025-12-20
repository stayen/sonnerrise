"""Tests for PersonaRepository."""

import pytest

from sonnerrise_personas import PersonaCreate, PersonaUpdate
from sonnerrise_personas.repository import PersonaNotFoundError


class TestPersonaRepository:
    """Tests for PersonaRepository."""

    def test_create(self, repo):
        """Test creating a persona."""
        data = PersonaCreate(
            name="Test Persona",
            style_of_music="epic orchestral",
        )
        persona = repo.create(data)

        assert persona.id is not None
        assert persona.name == "Test Persona"
        assert persona.style_of_music == "epic orchestral"
        assert persona.created_at is not None
        assert persona.updated_at is not None

    def test_get(self, repo):
        """Test getting a persona by ID."""
        created = repo.create(PersonaCreate(name="Get Test"))
        fetched = repo.get(created.id)

        assert fetched.id == created.id
        assert fetched.name == "Get Test"

    def test_get_not_found(self, repo):
        """Test getting non-existent persona."""
        with pytest.raises(PersonaNotFoundError) as exc_info:
            repo.get(9999)
        assert exc_info.value.persona_id == 9999

    def test_get_or_none(self, repo):
        """Test get_or_none returns None for missing."""
        result = repo.get_or_none(9999)
        assert result is None

    def test_get_or_none_found(self, repo):
        """Test get_or_none returns persona when found."""
        created = repo.create(PersonaCreate(name="Find Me"))
        result = repo.get_or_none(created.id)
        assert result is not None
        assert result.name == "Find Me"

    def test_update(self, repo):
        """Test updating a persona."""
        created = repo.create(PersonaCreate(name="Original"))
        updated = repo.update(created.id, PersonaUpdate(name="Updated"))

        assert updated.id == created.id
        assert updated.name == "Updated"

    def test_update_partial(self, repo):
        """Test partial update only changes specified fields."""
        created = repo.create(
            PersonaCreate(name="Original", style_of_music="rock")
        )
        updated = repo.update(created.id, PersonaUpdate(name="New Name"))

        assert updated.name == "New Name"
        assert updated.style_of_music == "rock"  # Unchanged

    def test_update_not_found(self, repo):
        """Test updating non-existent persona."""
        with pytest.raises(PersonaNotFoundError):
            repo.update(9999, PersonaUpdate(name="New"))

    def test_delete(self, repo):
        """Test deleting a persona."""
        created = repo.create(PersonaCreate(name="Delete Me"))
        result = repo.delete(created.id)

        assert result is True
        assert repo.get_or_none(created.id) is None

    def test_delete_not_found(self, repo):
        """Test deleting non-existent persona."""
        result = repo.delete(9999)
        assert result is False

    def test_list_empty(self, repo):
        """Test listing empty repository."""
        result = repo.list()

        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.pages == 1

    def test_list_with_items(self, repo):
        """Test listing with items."""
        for i in range(5):
            repo.create(PersonaCreate(name=f"Persona {i}"))

        result = repo.list()

        assert len(result.items) == 5
        assert result.total == 5

    def test_list_pagination(self, repo):
        """Test pagination."""
        for i in range(25):
            repo.create(PersonaCreate(name=f"Persona {i:02d}"))

        page1 = repo.list(page=1, per_page=10)
        page2 = repo.list(page=2, per_page=10)
        page3 = repo.list(page=3, per_page=10)

        assert len(page1.items) == 10
        assert len(page2.items) == 10
        assert len(page3.items) == 5
        assert page1.pages == 3
        assert page1.has_next is True
        assert page1.has_prev is False
        assert page3.has_next is False
        assert page3.has_prev is True

    def test_list_filter_by_name(self, repo):
        """Test filtering by name."""
        repo.create(PersonaCreate(name="Alpha Voice"))
        repo.create(PersonaCreate(name="Beta Voice"))
        repo.create(PersonaCreate(name="Alpha Style"))

        result = repo.list(name_filter="Alpha")

        assert len(result.items) == 2
        assert result.total == 2

    def test_search(self, repo):
        """Test searching personas."""
        repo.create(PersonaCreate(name="Epic Voice"))
        repo.create(PersonaCreate(name="Soft Voice"))
        repo.create(PersonaCreate(name="Epic Style"))

        results = repo.search("Epic")

        assert len(results) == 2
        names = [p.name for p in results]
        assert "Epic Voice" in names
        assert "Epic Style" in names

    def test_search_case_insensitive(self, repo):
        """Test that search is case-insensitive."""
        repo.create(PersonaCreate(name="UPPERCASE"))

        results = repo.search("uppercase")

        assert len(results) == 1
        assert results[0].name == "UPPERCASE"

    def test_count(self, repo):
        """Test counting personas."""
        assert repo.count() == 0

        for i in range(3):
            repo.create(PersonaCreate(name=f"Persona {i}"))

        assert repo.count() == 3

    def test_exists(self, repo):
        """Test checking if persona exists."""
        assert repo.exists(9999) is False

        created = repo.create(PersonaCreate(name="Exists"))
        assert repo.exists(created.id) is True
