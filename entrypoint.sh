#!/bin/bash
set -e

# Wait for database to be ready and initialize schema
sonnerrise-core init-db

# Start web server
exec sonnerrise-web --host 0.0.0.0 --port 5000
