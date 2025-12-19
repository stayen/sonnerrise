"""Tests for Definition models."""

from sonnerrise_core.config import Config, DatabaseConfig
from sonnerrise_core.database import get_database

from sonnerrise_definitions.models import (
    Definition,
    DefinitionLink,
    ModelVersion,
    PersonaType,
    ServiceType,
    VocalsType,
)


class TestDefinitionModel:
    """Tests for Definition SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert Definition.__tablename__ == "definitions"

    def test_columns_exist(self):
        """Test that all expected columns exist."""
        columns = {c.name for c in Definition.__table__.columns}
        expected = {
            "id", "title", "annotation", "service", "model",
            "style_of_music", "older_models_style", "lyrics",
            "persona_id", "persona_type", "vocals",
            "audio_influence", "style_influence", "weirdness",
            "cover_of_track_id", "comments",
            "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_repr(self):
        """Test string representation."""
        definition = Definition(title="Test Song")
        definition.id = 42
        assert "Definition" in repr(definition)
        assert "42" in repr(definition)
        assert "Test Song" in repr(definition)

    def test_persistence(self):
        """Test persisting a definition to database."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        db.create_tables()

        with db.session() as session:
            definition = Definition(
                title="Persistent Song",
                service=ServiceType.SUNO,
                model=ModelVersion.V4_0,
                style_of_music="pop, upbeat",
                vocals=VocalsType.ANY,
                audio_influence=25,
                style_influence=50,
                weirdness=50,
            )
            session.add(definition)
            session.commit()
            definition_id = definition.id

        with db.session() as session:
            loaded = session.query(Definition).get(definition_id)
            assert loaded is not None
            assert loaded.title == "Persistent Song"
            assert loaded.service == ServiceType.SUNO
            assert loaded.model == ModelVersion.V4_0

        db.close()


class TestDefinitionLinkModel:
    """Tests for DefinitionLink SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert DefinitionLink.__tablename__ == "definition_links"

    def test_persistence_with_definition(self):
        """Test persisting links with definition."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        db.create_tables()

        with db.session() as session:
            definition = Definition(
                title="Song with Links",
                service=ServiceType.SUNO,
                model=ModelVersion.V4_0,
                style_of_music="rock",
                vocals=VocalsType.ANY,
                audio_influence=25,
                style_influence=50,
                weirdness=50,
            )
            session.add(definition)
            session.flush()

            link = DefinitionLink(
                definition_id=definition.id,
                url="https://example.com",
                description="Example link",
            )
            session.add(link)
            session.commit()
            definition_id = definition.id

        with db.session() as session:
            loaded = session.query(Definition).get(definition_id)
            assert len(loaded.links) == 1
            assert loaded.links[0].url == "https://example.com"

        db.close()


class TestEnums:
    """Tests for enum types."""

    def test_service_type(self):
        """Test ServiceType enum."""
        assert ServiceType.SUNO.value == "suno"

    def test_model_version(self):
        """Test ModelVersion enum."""
        assert ModelVersion.V3_5.value == "v3.5"
        assert ModelVersion.V4_0.value == "v4.0"
        assert ModelVersion.V4_5_PLUS.value == "v4.5+"
        assert ModelVersion.V5_0.value == "v5.0"

    def test_persona_type(self):
        """Test PersonaType enum."""
        assert PersonaType.VOICE.value == "voice"
        assert PersonaType.STYLE.value == "style"

    def test_vocals_type(self):
        """Test VocalsType enum."""
        assert VocalsType.ANY.value == "any"
        assert VocalsType.FEMALE.value == "female"
        assert VocalsType.MALE.value == "male"
