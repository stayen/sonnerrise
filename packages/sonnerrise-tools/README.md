# sonnerrise-tools

Tools module for the Sonnerrise suite - database export/import utilities.

## Features

- Export entire database to JSON or YAML files
- Import data from backup files
- Automatic schema versioning and migration
- Selective export/import by entity type
- Data validation on import

## Installation

```bash
pip install sonnerrise-tools
```

## Usage

### Python API

```python
from sonnerrise_core import load_config, get_database
from sonnerrise_tools import ExportService, ImportService

config = load_config()
db = get_database(config)

# Export all data
exporter = ExportService(db)
exporter.export_all("backup.json")

# Export specific entities
exporter.export_personas("personas.json")
exporter.export_tracks("tracks.yaml", format="yaml")

# Import data
importer = ImportService(db)
result = importer.import_all("backup.json")
print(f"Imported {result.total_records} records")

# Import with options
result = importer.import_all(
    "backup.json",
    skip_existing=True,  # Skip records that already exist
    create_tables=True,   # Create missing tables
)
```

### CLI

```bash
# Export all data to JSON
sonnerrise-tools export backup.json

# Export to YAML
sonnerrise-tools export backup.yaml --format yaml

# Export specific entities
sonnerrise-tools export personas.json --only personas
sonnerrise-tools export tracks.json --only tracks,definitions

# Import data
sonnerrise-tools import backup.json

# Import with options
sonnerrise-tools import backup.json --skip-existing --create-tables

# Show backup info
sonnerrise-tools info backup.json

# Validate backup without importing
sonnerrise-tools validate backup.json
```

## Export Format

The export file contains all entities with their relationships:

```json
{
  "version": "1.0",
  "created_at": "2024-03-15T10:30:00",
  "entities": {
    "personas": [...],
    "definitions": [...],
    "definition_links": [...],
    "tracks": [...],
    "track_links": [...],
    "track_events": [...],
    "promos": [...],
    "promo_links": [...]
  },
  "counts": {
    "personas": 10,
    "definitions": 25,
    "tracks": 50,
    ...
  }
}
```

## Migration Support

When importing data with a different schema version:
- Missing tables are automatically created
- New columns use default values
- Removed columns are ignored
- Data validation ensures integrity
