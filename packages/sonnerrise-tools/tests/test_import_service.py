"""Tests for ImportService."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sonnerrise_tools import ExportService, ImportService
from sonnerrise_tools.schemas import ImportOptions


class TestImportService:
    """Tests for ImportService."""

    def test_get_backup_info(self, session, temp_dir: Path, sample_persona):
        """Test getting backup file information."""
        # First export data
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"
        exporter.export_all(output_path)

        # Get backup info
        importer = ImportService(session)
        info = importer.get_backup_info(output_path)

        assert info.version == "1.0"
        assert info.is_compatible
        assert info.counts.personas == 1
        assert info.file_size > 0

    def test_validate_backup(self, session, temp_dir: Path, sample_persona):
        """Test validating backup file."""
        # First export data
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"
        exporter.export_all(output_path)

        # Validate
        importer = ImportService(session)
        result = importer.validate(output_path)

        assert result.success
        assert result.total_records == 1

    def test_validate_invalid_json(self, session, temp_dir: Path):
        """Test validating invalid JSON file."""
        invalid_path = temp_dir / "invalid.json"
        invalid_path.write_text("not valid json {")

        importer = ImportService(session)
        result = importer.validate(invalid_path)

        assert not result.success
        assert len(result.errors) > 0

    def test_import_all(self, session, temp_dir: Path, sample_promo):
        """Test importing all data."""
        # Export data
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"
        exporter.export_all(output_path)

        # Clear and reimport
        from sonnerrise_personas import Persona
        from sonnerrise_definitions import Definition
        from sonnerrise_tracks import Track
        from sonnerrise_promo import Promo

        session.query(Promo).delete()
        session.query(Track).delete()
        session.query(Definition).delete()
        session.query(Persona).delete()
        session.commit()

        # Verify cleared
        assert session.query(Persona).count() == 0

        # Import
        importer = ImportService(session)
        options = ImportOptions(create_tables=True)
        result = importer.import_all(output_path, options=options)

        assert result.success
        assert result.imported.personas == 1
        assert result.imported.definitions == 1
        assert result.imported.tracks == 1
        assert result.imported.promos == 1

    def test_import_skip_existing(self, session, temp_dir: Path, sample_persona):
        """Test importing with skip_existing option."""
        # Export data
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"
        exporter.export_all(output_path)

        # Import with skip_existing - should skip the existing persona
        importer = ImportService(session)
        options = ImportOptions(skip_existing=True)
        result = importer.import_all(output_path, options=options)

        assert result.success
        assert result.skipped.personas == 1
        assert result.imported.personas == 0

    def test_import_clear_existing(self, session, temp_dir: Path, sample_persona):
        """Test importing with clear_existing option."""
        # Export data
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"
        exporter.export_all(output_path)

        # Create another persona that should be cleared
        from sonnerrise_personas import Persona

        another = Persona(name="Another Persona", style_of_music="Jazz")
        session.add(another)
        session.commit()

        # Verify we have 2 personas
        assert session.query(Persona).count() == 2

        # Import with clear_existing
        importer = ImportService(session)
        options = ImportOptions(clear_existing=True)
        result = importer.import_all(output_path, options=options)

        # Should have cleared then imported only the backup data
        assert result.success
        assert session.query(Persona).count() == 1

    def test_import_incompatible_version(self, session, temp_dir: Path):
        """Test importing backup with incompatible version."""
        backup_path = temp_dir / "backup.json"
        backup_path.write_text(json.dumps({
            "version": "2.0",
            "created_at": "2024-01-01T00:00:00",
            "entities": {},
            "counts": {},
        }))

        importer = ImportService(session)
        result = importer.import_all(backup_path)

        assert not result.success
        assert any("Incompatible" in e for e in result.errors)

    def test_import_yaml(self, session, temp_dir: Path, sample_persona):
        """Test importing YAML backup."""
        # Export to YAML
        exporter = ExportService(session)
        output_path = temp_dir / "backup.yaml"
        exporter.export_all(output_path, format="yaml")

        # Clear and reimport
        from sonnerrise_personas import Persona

        session.query(Persona).delete()
        session.commit()

        # Import YAML
        importer = ImportService(session)
        result = importer.import_all(output_path)

        assert result.success
        assert result.imported.personas == 1


class TestRoundTrip:
    """Test export and import round-trip."""

    def test_full_round_trip(self, session, temp_dir: Path, sample_promo):
        """Test exporting and importing preserves all data."""
        from sonnerrise_personas import Persona
        from sonnerrise_definitions import Definition
        from sonnerrise_tracks import Track
        from sonnerrise_promo import Promo

        # Get original data
        original_persona = session.query(Persona).first()
        original_name = original_persona.name

        # Export
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"
        exporter.export_all(output_path)

        # Clear database
        session.query(Promo).delete()
        session.query(Track).delete()
        session.query(Definition).delete()
        session.query(Persona).delete()
        session.commit()

        # Import
        importer = ImportService(session)
        result = importer.import_all(output_path)

        assert result.success

        # Verify data restored
        restored_persona = session.query(Persona).first()
        assert restored_persona.name == original_name
