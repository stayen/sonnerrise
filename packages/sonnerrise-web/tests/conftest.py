"""Test fixtures for sonnerrise-web."""

from __future__ import annotations

from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from sonnerrise_core.models import BaseModel, import_all_models


@pytest.fixture
def engine():
    """Create in-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:")
    import_all_models()
    BaseModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    """Create database session."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def app(engine, session) -> Flask:
    """Create Flask test application."""
    from sonnerrise_core import DatabaseConfig, SonnerriseConfig
    from sonnerrise_web.app import create_app

    # Create a mock config
    config = SonnerriseConfig(
        database=DatabaseConfig(plugin="sqlite", database=":memory:")
    )

    app = create_app(config)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Override database session
    app.database._engine = engine

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_persona(session: Session):
    """Create sample persona."""
    from sonnerrise_personas import Persona

    persona = Persona(
        name="Test Persona",
        style_of_music="Electronic",
        comments="Test comments",
    )
    session.add(persona)
    session.commit()
    session.refresh(persona)
    return persona


@pytest.fixture
def sample_definition(session: Session, sample_persona):
    """Create sample definition."""
    from sonnerrise_definitions import Definition, ServiceType, ModelVersion, PersonaType, VocalsType

    definition = Definition(
        title="Test Definition",
        service=ServiceType.SUNO,
        model=ModelVersion.V4_0,
        persona_type=PersonaType.VOICE,
        persona_id=sample_persona.id,
        vocals=VocalsType.ANY,
        style_of_music="Electronic, Synth",
    )
    session.add(definition)
    session.commit()
    session.refresh(definition)
    return definition


@pytest.fixture
def sample_track(session: Session, sample_definition):
    """Create sample track."""
    from sonnerrise_tracks import Track

    track = Track(
        title="Test Track",
        definition_id=sample_definition.id,
    )
    session.add(track)
    session.commit()
    session.refresh(track)
    return track


@pytest.fixture
def sample_promo(session: Session, sample_track):
    """Create sample promo."""
    from sonnerrise_promo import Promo

    promo = Promo(
        track_id=sample_track.id,
        pitch="Test pitch",
    )
    session.add(promo)
    session.commit()
    session.refresh(promo)
    return promo
