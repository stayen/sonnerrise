"""Tests for sonnerrise-tools schemas."""

from __future__ import annotations

from datetime import datetime

import pytest

from sonnerrise_tools.schemas import (
    BackupData,
    BackupEntities,
    BackupInfo,
    EntityCounts,
    ExportOptions,
    ImportOptions,
    ImportResult,
    SCHEMA_VERSION,
)


class TestEntityCounts:
    """Tests for EntityCounts."""

    def test_default_values(self):
        """Test default values are zero."""
        counts = EntityCounts()

        assert counts.personas == 0
        assert counts.definitions == 0
        assert counts.tracks == 0
        assert counts.promos == 0
        assert counts.total == 0

    def test_total_calculation(self):
        """Test total calculation."""
        counts = EntityCounts(
            personas=5,
            definitions=10,
            definition_links=3,
            tracks=20,
            track_links=5,
            track_events=8,
            promos=15,
            promo_links=4,
        )

        assert counts.total == 70


class TestBackupEntities:
    """Tests for BackupEntities."""

    def test_default_empty_lists(self):
        """Test default values are empty lists."""
        entities = BackupEntities()

        assert entities.personas == []
        assert entities.definitions == []
        assert entities.tracks == []
        assert entities.promos == []


class TestBackupData:
    """Tests for BackupData."""

    def test_default_values(self):
        """Test default values."""
        backup = BackupData()

        assert backup.version == SCHEMA_VERSION
        assert isinstance(backup.created_at, datetime)
        assert isinstance(backup.entities, BackupEntities)
        assert isinstance(backup.counts, EntityCounts)

    def test_update_counts(self):
        """Test update_counts method."""
        entities = BackupEntities(
            personas=[{"id": 1}, {"id": 2}],
            definitions=[{"id": 1}],
            tracks=[{"id": 1}, {"id": 2}, {"id": 3}],
        )
        backup = BackupData(entities=entities)

        backup.update_counts()

        assert backup.counts.personas == 2
        assert backup.counts.definitions == 1
        assert backup.counts.tracks == 3
        assert backup.counts.promos == 0


class TestImportResult:
    """Tests for ImportResult."""

    def test_default_success(self):
        """Test default is success."""
        result = ImportResult()

        assert result.success is True
        assert result.total_records == 0
        assert result.has_errors is False
        assert result.has_warnings is False

    def test_has_errors(self):
        """Test has_errors property."""
        result = ImportResult()
        result.errors.append("An error occurred")

        assert result.has_errors is True

    def test_has_warnings(self):
        """Test has_warnings property."""
        result = ImportResult()
        result.warnings.append("A warning")

        assert result.has_warnings is True


class TestExportOptions:
    """Tests for ExportOptions."""

    def test_default_include_all(self):
        """Test default includes all entities."""
        options = ExportOptions()

        assert options.include_personas is True
        assert options.include_definitions is True
        assert options.include_tracks is True
        assert options.include_promos is True
        assert options.pretty_print is True


class TestImportOptions:
    """Tests for ImportOptions."""

    def test_default_values(self):
        """Test default values."""
        options = ImportOptions()

        assert options.skip_existing is False
        assert options.create_tables is True
        assert options.validate_only is False
        assert options.clear_existing is False


class TestBackupInfo:
    """Tests for BackupInfo."""

    def test_is_compatible_v1(self):
        """Test version 1.x is compatible."""
        info = BackupInfo(
            version="1.0",
            created_at=datetime.now(),
            counts=EntityCounts(),
            file_path="/path/to/backup.json",
            file_size=1024,
        )

        assert info.is_compatible is True

    def test_is_compatible_v1_minor(self):
        """Test version 1.x with minor version is compatible."""
        info = BackupInfo(
            version="1.5",
            created_at=datetime.now(),
            counts=EntityCounts(),
            file_path="/path/to/backup.json",
            file_size=1024,
        )

        assert info.is_compatible is True

    def test_is_incompatible_v2(self):
        """Test version 2.x is incompatible."""
        info = BackupInfo(
            version="2.0",
            created_at=datetime.now(),
            counts=EntityCounts(),
            file_path="/path/to/backup.json",
            file_size=1024,
        )

        assert info.is_compatible is False
