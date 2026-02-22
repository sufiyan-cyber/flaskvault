"""Application configuration.

Reads settings from environment variables with sensible defaults
so the app works locally (SQLite) and in production (PostgreSQL).
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Security -----------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-before-deploying")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # In production, set SESSION_COOKIE_SECURE=True (requires HTTPS)

    # --- Database -----------------------------------------------------------
    # If DATABASE_URL is set (e.g. on Render) → use PostgreSQL.
    # Otherwise → fall back to a local SQLite file inside instance/.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db"),
    )
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File uploads -------------------------------------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "txt", "csv", "docx", "xlsx", "zip"}
