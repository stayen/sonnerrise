"""Tests for DefinitionRepository."""

import pytest

from sonnerrise_definitions import (
    DefinitionCreate,
    DefinitionFilter,
    DefinitionUpdate,
    LinkCreate,
    ModelVersion,
    PersonaType,
    VocalsType,
)
from sonnerrise_definitions.repository import DefinitionNotFoundError


class TestDefinitionRepository:
    """Tests for DefinitionRepository."""

    def test_create_minimal(self, repo):
        """Test creating a definition with minimal fields."""
        data = DefinitionCreate(
            title="Test Definition",
            style_of_music="pop, upbeat",
        )
        definition = repo.create(data)

        assert definition.id is not None
        assert definition.title == "Test Definition"
        assert definition.style_of_music == "pop, upbeat"
        assert definition.model == ModelVersion.V4_0
        assert definition.vocals == VocalsType.ANY
        assert definition.audio_influence == 25
        assert definition.style_influence == 50
        assert definition.weirdness == 50

    def test_create_with_links(self, repo):
        """Test creating a definition with links."""
        data = DefinitionCreate(
            title="Linked Definition",
            style_of_music="rock",
            links=[
                LinkCreate(url="https://example.com/1", description="Link 1"),
                LinkCreate(url="https://example.com/2", description="Link 2"),
            ],
        )
        definition = repo.create(data)

        assert len(definition.links) == 2
        assert definition.links[0].url == "https://example.com/1"

    def test_get(self, repo):
        """Test getting a definition by ID."""
        created = repo.create(
            DefinitionCreate(title="Get Test", style_of_music="jazz")
        )
        fetched = repo.get(created.id)

        assert fetched.id == created.id
        assert fetched.title == "Get Test"

    def test_get_not_found(self, repo):
        """Test getting non-existent definition."""
        with pytest.raises(DefinitionNotFoundError) as exc_info:
            repo.get(9999)
        assert exc_info.value.definition_id == 9999

    def test_get_or_none(self, repo):
        """Test get_or_none returns None for missing."""
        result = repo.get_or_none(9999)
        assert result is None

    def test_update(self, repo):
        """Test updating a definition."""
        created = repo.create(
            DefinitionCreate(title="Original", style_of_music="pop")
        )
        updated = repo.update(
            created.id,
            DefinitionUpdate(title="Updated", model=ModelVersion.V5_0),
        )

        assert updated.id == created.id
        assert updated.title == "Updated"
        assert updated.model == ModelVersion.V5_0
        assert updated.style_of_music == "pop"  # Unchanged

    def test_update_links(self, repo):
        """Test updating definition links."""
        created = repo.create(
            DefinitionCreate(
                title="Test",
                style_of_music="pop",
                links=[LinkCreate(url="https://old.com")],
            )
        )
        updated = repo.update(
            created.id,
            DefinitionUpdate(links=[LinkCreate(url="https://new.com")]),
        )

        assert len(updated.links) == 1
        assert updated.links[0].url == "https://new.com"

    def test_delete(self, repo):
        """Test deleting a definition."""
        created = repo.create(
            DefinitionCreate(title="Delete Me", style_of_music="delete")
        )
        result = repo.delete(created.id)

        assert result is True
        assert repo.get_or_none(created.id) is None

    def test_delete_not_found(self, repo):
        """Test deleting non-existent definition."""
        result = repo.delete(9999)
        assert result is False

    def test_list_empty(self, repo):
        """Test listing empty repository."""
        result = repo.list()

        assert result.items == []
        assert result.total == 0
        assert result.page == 1

    def test_list_with_items(self, repo):
        """Test listing with items."""
        for i in range(5):
            repo.create(
                DefinitionCreate(title=f"Definition {i}", style_of_music="test")
            )

        result = repo.list()

        assert len(result.items) == 5
        assert result.total == 5

    def test_list_pagination(self, repo):
        """Test pagination."""
        for i in range(25):
            repo.create(
                DefinitionCreate(title=f"Definition {i:02d}", style_of_music="test")
            )

        page1 = repo.list(page=1, per_page=10)
        page2 = repo.list(page=2, per_page=10)
        page3 = repo.list(page=3, per_page=10)

        assert len(page1.items) == 10
        assert len(page2.items) == 10
        assert len(page3.items) == 5
        assert page1.pages == 3

    def test_list_filter_by_title(self, repo):
        """Test filtering by title."""
        repo.create(DefinitionCreate(title="Alpha Song", style_of_music="pop"))
        repo.create(DefinitionCreate(title="Beta Song", style_of_music="rock"))
        repo.create(DefinitionCreate(title="Alpha Tune", style_of_music="jazz"))

        result = repo.list(filters=DefinitionFilter(title="Alpha"))

        assert len(result.items) == 2
        assert result.total == 2

    def test_list_filter_by_model(self, repo):
        """Test filtering by model."""
        repo.create(
            DefinitionCreate(title="V4 Song", style_of_music="pop", model=ModelVersion.V4_0)
        )
        repo.create(
            DefinitionCreate(title="V5 Song", style_of_music="rock", model=ModelVersion.V5_0)
        )

        result = repo.list(filters=DefinitionFilter(model=ModelVersion.V5_0))

        assert len(result.items) == 1
        assert result.items[0].model == ModelVersion.V5_0

    def test_list_filter_by_vocals(self, repo):
        """Test filtering by vocals."""
        repo.create(
            DefinitionCreate(title="Any", style_of_music="pop", vocals=VocalsType.ANY)
        )
        repo.create(
            DefinitionCreate(title="Female", style_of_music="rock", vocals=VocalsType.FEMALE)
        )

        result = repo.list(filters=DefinitionFilter(vocals=VocalsType.FEMALE))

        assert len(result.items) == 1

    def test_search(self, repo):
        """Test searching definitions."""
        repo.create(DefinitionCreate(title="Epic Battle", style_of_music="orchestral"))
        repo.create(DefinitionCreate(title="Soft Ballad", style_of_music="acoustic"))
        repo.create(DefinitionCreate(title="Rock Epic", style_of_music="rock"))

        results = repo.search("Epic")

        assert len(results) == 2

    def test_search_in_style(self, repo):
        """Test searching in style_of_music."""
        repo.create(DefinitionCreate(title="Song 1", style_of_music="epic orchestral"))
        repo.create(DefinitionCreate(title="Song 2", style_of_music="soft acoustic"))

        results = repo.search("orchestral")

        assert len(results) == 1
        assert results[0].title == "Song 1"

    def test_count(self, repo):
        """Test counting definitions."""
        assert repo.count() == 0

        for i in range(3):
            repo.create(
                DefinitionCreate(title=f"Definition {i}", style_of_music="test")
            )

        assert repo.count() == 3

    def test_exists(self, repo):
        """Test checking if definition exists."""
        assert repo.exists(9999) is False

        created = repo.create(
            DefinitionCreate(title="Exists", style_of_music="test")
        )
        assert repo.exists(created.id) is True

    def test_add_link(self, repo):
        """Test adding a link to a definition."""
        created = repo.create(
            DefinitionCreate(title="Test", style_of_music="pop")
        )
        updated = repo.add_link(created.id, "https://new-link.com", "New link")

        assert len(updated.links) == 1
        assert updated.links[0].url == "https://new-link.com"

    def test_remove_link(self, repo):
        """Test removing a link from a definition."""
        created = repo.create(
            DefinitionCreate(
                title="Test",
                style_of_music="pop",
                links=[LinkCreate(url="https://remove.com")],
            )
        )
        link_id = created.links[0].id
        updated = repo.remove_link(created.id, link_id)

        assert len(updated.links) == 0
