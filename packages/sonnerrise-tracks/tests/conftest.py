"""Pytest configuration and fixtures for sonnerrise-tracks tests."""

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
def repo(db):
    """Create a TrackRepository with test database."""
    from sonnerrise_tracks import TrackRepository

    return TrackRepository(db)
