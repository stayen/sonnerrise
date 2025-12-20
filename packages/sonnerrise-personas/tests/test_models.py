"""Tests for Persona model."""

from sonnerrise_core.config import Config, DatabaseConfig
from sonnerrise_core.database import get_database
from sonnerrise_core.models import import_all_models

from sonnerrise_personas.models import Persona


class TestPersonaModel:
    """Tests for Persona SQLAlchemy model."""

    def test_table_name(self):
        """Test that table name is correct."""
        assert Persona.__tablename__ == "personas"

    def test_columns_exist(self):
        """Test that all expected columns exist."""
        columns = {c.name for c in Persona.__table__.columns}
        expected = {"id", "name", "style_of_music", "parental_track_id",
                    "comments", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_repr(self):
        """Test string representation."""
        persona = Persona(name="Test")
        persona.id = 42
        assert "Persona" in repr(persona)
        assert "42" in repr(persona)
        assert "Test" in repr(persona)

    def test_persistence(self):
        """Test persisting a persona to database."""
        config = Config(
            database=DatabaseConfig(plugin="sqlite", database=":memory:")
        )
        db = get_database(config)
        import_all_models()
        db.create_tables()

        with db.session() as session:
            persona = Persona(
                name="Persistent Persona",
                style_of_music="ambient",
                comments="Test comment",
            )
            session.add(persona)
            session.commit()
            persona_id = persona.id

        with db.session() as session:
            loaded = session.query(Persona).get(persona_id)
            assert loaded is not None
            assert loaded.name == "Persistent Persona"
            assert loaded.style_of_music == "ambient"
            assert loaded.comments == "Test comment"
            assert loaded.parental_track_id is None

        db.close()
