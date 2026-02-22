"""Application factory for the Flask app.

Usage:
    from app import create_app
    app = create_app()
"""

import os
import click
from flask import Flask, render_template

from config import Config
from app.extensions import db, login_manager, csrf
from app.models import User  # noqa: F401 – imported so SQLAlchemy knows the model


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )
    app.config.from_object(config_class)

    # ── Initialise extensions ──────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ── User loader for Flask-Login ────────────────────────────────────
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Register blueprints ────────────────────────────────────────────
    from app.auth import auth as auth_bp
    from app.routes import main as main_bp
    from app.files import files as files_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp)

    # ── Ensure upload directory exists ─────────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Custom error pages ─────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    # ── CLI command: flask init-db ─────────────────────────────────────
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        click.echo("✅ Database tables created.")

    return app
