"""Pytest configuration and fixtures for sonnerrise-definitions tests."""

import pytest

from sonnerrise_core.config import Config, DatabaseConfig
from sonnerrise_core.database import get_database


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
    database.create_tables()
    yield database
    database.close()


@pytest.fixture
def repo(db):
    """Create a DefinitionRepository with test database."""
    from sonnerrise_definitions import DefinitionRepository

    return DefinitionRepository(db)
