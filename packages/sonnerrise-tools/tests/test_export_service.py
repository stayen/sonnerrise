"""Tests for ExportService."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from sonnerrise_tools import ExportService
from sonnerrise_tools.schemas import ExportOptions


class TestExportService:
    """Tests for ExportService."""

    def test_export_empty_database(self, session, temp_dir: Path):
        """Test exporting empty database."""
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"

        backup = exporter.export_all(output_path)

        assert backup.counts.total == 0
        assert output_path.exists()

        # Verify file contents
        with open(output_path) as f:
            data = json.load(f)
        assert data["version"] == "1.0"
        assert "entities" in data
        assert "counts" in data

    def test_export_with_personas(self, session, temp_dir: Path, sample_persona):
        """Test exporting with personas."""
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"

        backup = exporter.export_all(output_path)

        assert backup.counts.personas == 1
        assert len(backup.entities.personas) == 1
        assert backup.entities.personas[0]["name"] == "Test Persona"

    def test_export_with_all_entities(
        self, session, temp_dir: Path, sample_promo
    ):
        """Test exporting with all entity types."""
        # sample_promo fixture creates persona -> definition -> track -> promo
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"

        backup = exporter.export_all(output_path)

        assert backup.counts.personas == 1
        assert backup.counts.definitions == 1
        assert backup.counts.tracks == 1
        assert backup.counts.promos == 1

    def test_export_to_yaml(self, session, temp_dir: Path, sample_persona):
        """Test exporting to YAML format."""
        exporter = ExportService(session)
        output_path = temp_dir / "backup.yaml"

        backup = exporter.export_all(output_path, format="yaml")

        assert output_path.exists()
        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert data["version"] == "1.0"
        assert len(data["entities"]["personas"]) == 1

    def test_export_selective_entities(self, session, temp_dir: Path, sample_promo):
        """Test exporting only specific entities."""
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"

        options = ExportOptions(
            include_personas=True,
            include_definitions=False,
            include_tracks=False,
            include_promos=False,
        )

        backup = exporter.export_all(output_path, options=options)

        assert backup.counts.personas == 1
        assert backup.counts.definitions == 0
        assert backup.counts.tracks == 0
        assert backup.counts.promos == 0

    def test_export_personas_only(self, session, temp_dir: Path, sample_persona):
        """Test export_personas convenience method."""
        exporter = ExportService(session)
        output_path = temp_dir / "personas.json"

        backup = exporter.export_personas(output_path)

        assert backup.counts.personas == 1
        assert backup.counts.definitions == 0

    def test_export_compact(self, session, temp_dir: Path, sample_persona):
        """Test compact export (no pretty printing)."""
        exporter = ExportService(session)
        output_path = temp_dir / "backup.json"

        options = ExportOptions(pretty_print=False)
        exporter.export_all(output_path, options=options)

        # Compact JSON has no newlines inside
        with open(output_path) as f:
            content = f.read()
        # Compact output should be a single line
        assert content.count("\n") <= 1

    def test_export_creates_parent_directories(self, session, temp_dir: Path):
        """Test that export creates missing parent directories."""
        exporter = ExportService(session)
        output_path = temp_dir / "nested" / "dir" / "backup.json"

        exporter.export_all(output_path)

        assert output_path.exists()
