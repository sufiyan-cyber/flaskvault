"""WSGI entry point.

For local development:
    python wsgi.py

For production (gunicorn):
    gunicorn wsgi:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Create tables automatically during local development
    with app.app_context():
        from app.extensions import db
        db.create_all()
    app.run(debug=True)
