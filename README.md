# Sonnerrise

Suno track management and promotion planning suite. Provides tools for cataloging AI-generated audio tracks, managing generation definitions, scheduling promotional events, and organizing release workflows.

## Features

- **Definitions**: Store and organize Suno generation parameters (prompts, styles, lyrics, model settings)
- **Personas**: Manage voice/style references for consistent generation
- **Tracks**: Catalog generated tracks with metadata, lyrics, cover art, and event scheduling
- **Promotions**: Create promotional materials including AI art prompts and marketing copy
- **Calendar**: View and manage track events in weekly/monthly formats
- **Tools**: Export/import database backups

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/stayen/sonnerrise.git
cd sonnerrise

# Create environment file
cp .env.example .env
# Edit .env to set passwords and secret key

# Start services
docker-compose up -d

# Access web interface
open http://localhost:5000
```

### Option 2: Manual Installation

Requirements: Python 3.11+, MySQL 8.0+
```bash
git clone https://github.com/stayen/sonnerrise.git
cd sonnerrise

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install packages
pip install -e packages/sonnerrise-core
pip install -e packages/sonnerrise-personas
pip install -e packages/sonnerrise-definitions
pip install -e packages/sonnerrise-tracks
pip install -e packages/sonnerrise-promo
pip install -e packages/sonnerrise-calendar
pip install -e packages/sonnerrise-tools
pip install -e packages/sonnerrise-web

# Create configuration
cp config/sonnerrise.yaml.example config/sonnerrise.yaml
# Edit config/sonnerrise.yaml with database credentials

# Initialize database
sonnerrise-core init-db

# Run web server
sonnerrise-web --host 127.0.0.1 --port 5000
```

## Configuration

Copy `config/sonnerrise.yaml.example` to `config/sonnerrise.yaml` and adjust:
```yaml
database:
  plugin: mysql
  host: localhost
  port: 3306
  user: sonnerrise
  password: your-password
  database: sonnerrise

web:
  host: 0.0.0.0
  port: 5000
  secret_key: generate-a-random-key
```

Environment variables override configuration file values. See `packages/sonnerrise-core/README.md` for the full list.

## Modules

| Package | Description |
|---------|-------------|
| `sonnerrise-core` | Configuration loader, database abstraction |
| `sonnerrise-personas` | Persona (voice/style reference) management |
| `sonnerrise-definitions` | Suno generation definitions |
| `sonnerrise-tracks` | Track catalog with events |
| `sonnerrise-promo` | Promotional materials |
| `sonnerrise-calendar` | Event calendar views |
| `sonnerrise-tools` | Database export/import |
| `sonnerrise-web` | Flask web interface |

Each module provides both a Python API and CLI. Run `<module-name> --help` for available commands.

## Documentation

- Full specification: `docs/SPEC.md`
- Module documentation: `packages/<module>/README.md`

## License

MIT
