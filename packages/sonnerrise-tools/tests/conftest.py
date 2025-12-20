"""Test fixtures for sonnerrise-tools."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
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
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


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
        name="Test Definition",
        service_type=ServiceType.SUNO,
        model_version=ModelVersion.V4,
        persona_type=PersonaType.PERSONA,
        persona_id=sample_persona.id,
        vocals_type=VocalsType.MALE,
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
