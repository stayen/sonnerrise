"""Pytest configuration and fixtures for sonnerrise-promo tests."""

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
    """Create a PromoRepository with test database."""
    from sonnerrise_promo import PromoRepository

    return PromoRepository(db)


@pytest.fixture
def track(db):
    """Create a test track."""
    from sonnerrise_tracks.models import Track

    with db.session() as session:
        track = Track(title="Test Track")
        session.add(track)
        session.commit()
        return track.id
