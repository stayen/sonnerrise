"""Tests for Flask application."""

from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient


class TestAppFactory:
    """Tests for application factory."""

    def test_create_app(self, app: Flask):
        """Test app creation."""
        assert app is not None
        assert app.config["TESTING"] is True

    def test_app_has_blueprints(self, app: Flask):
        """Test that all blueprints are registered."""
        blueprint_names = list(app.blueprints.keys())

        assert "home" in blueprint_names
        assert "personas" in blueprint_names
        assert "definitions" in blueprint_names
        assert "tracks" in blueprint_names
        assert "promo" in blueprint_names
        assert "calendar" in blueprint_names
        assert "tools" in blueprint_names


class TestHomeViews:
    """Tests for home views."""

    def test_home_page(self, client: FlaskClient):
        """Test home page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Dashboard" in response.data


class TestPersonasViews:
    """Tests for personas views."""

    def test_personas_list(self, client: FlaskClient):
        """Test personas list page."""
        response = client.get("/personas/")
        assert response.status_code == 200
        assert b"Personas" in response.data

    def test_personas_create_page(self, client: FlaskClient):
        """Test personas create page loads."""
        response = client.get("/personas/new")
        assert response.status_code == 200
        assert b"New Persona" in response.data


class TestDefinitionsViews:
    """Tests for definitions views."""

    def test_definitions_list(self, client: FlaskClient):
        """Test definitions list page."""
        response = client.get("/definitions/")
        assert response.status_code == 200
        assert b"Definitions" in response.data

    def test_definitions_create_page(self, client: FlaskClient):
        """Test definitions create page loads."""
        response = client.get("/definitions/new")
        assert response.status_code == 200
        assert b"New Definition" in response.data


class TestTracksViews:
    """Tests for tracks views."""

    def test_tracks_list(self, client: FlaskClient):
        """Test tracks list page."""
        response = client.get("/tracks/")
        assert response.status_code == 200
        assert b"Tracks" in response.data

    def test_tracks_create_page(self, client: FlaskClient):
        """Test tracks create page loads."""
        response = client.get("/tracks/new")
        assert response.status_code == 200
        assert b"New Track" in response.data


class TestPromoViews:
    """Tests for promo views."""

    def test_promo_list(self, client: FlaskClient):
        """Test promo list page."""
        response = client.get("/promo/")
        assert response.status_code == 200
        assert b"Promotions" in response.data


class TestCalendarViews:
    """Tests for calendar views."""

    def test_calendar_month_view(self, client: FlaskClient):
        """Test calendar month view."""
        response = client.get("/calendar/")
        assert response.status_code == 200
        assert b"Calendar" in response.data

    def test_calendar_week_view(self, client: FlaskClient):
        """Test calendar week view."""
        response = client.get("/calendar/?view=week")
        assert response.status_code == 200
        assert b"Calendar" in response.data


class TestToolsViews:
    """Tests for tools views."""

    def test_tools_page(self, client: FlaskClient):
        """Test tools page."""
        response = client.get("/tools/")
        assert response.status_code == 200
        assert b"Tools" in response.data
        assert b"Export" in response.data
        assert b"Import" in response.data
