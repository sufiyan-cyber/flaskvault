"""Main blueprint — public pages and the user dashboard."""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import File

main = Blueprint("main", __name__)


@main.route("/")
def home():
    """Landing page."""
    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():
    """Authenticated user dashboard with quick stats."""
    file_count = db.session.execute(
        db.select(db.func.count(File.id)).where(File.owner_id == current_user.id)
    ).scalar() or 0
    return render_template("dashboard.html", file_count=file_count)
