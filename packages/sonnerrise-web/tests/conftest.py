"""Test fixtures for sonnerrise-web."""

from __future__ import annotations

from datetime import datetime
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from sonnerrise_core.models import BaseModel


@pytest.fixture
def engine():
    """Create in-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:")
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
    from sonnerrise_core import SonnerriseConfig
    from sonnerrise_web.app import create_app

    # Create a mock config
    config = SonnerriseConfig(
        database={"type": "sqlite", "path": ":memory:"}
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
    from sonnerrise_definitions import Definition

    definition = Definition(
        name="Test Definition",
        service_type="suno",
        model_version="v4.0",
        persona_type="voice",
        persona_id=sample_persona.id,
        vocals_type="any",
        style="Electronic, Synth",
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
        generation_date=datetime.now(),
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
        summary="Test summary",
    )
    session.add(promo)
    session.commit()
    session.refresh(promo)
    return promo
