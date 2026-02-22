"""Files blueprint — upload, list, download, delete."""

import os
import uuid
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, current_app, send_from_directory, abort,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import File

files = Blueprint("files", __name__, url_prefix="/files")


def _allowed_file(filename: str) -> bool:
    """Return True if filename has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@files.route("/")
@login_required
def file_list():
    """Show all files owned by the current user."""
    user_files = db.session.execute(
        db.select(File)
        .where(File.owner_id == current_user.id)
        .order_by(File.upload_date.desc())
    ).scalars().all()
    return render_template("files.html", files=user_files)


@files.route("/upload", methods=["POST"])
@login_required
def upload():
    """Handle file upload."""
    if "file" not in request.files:
        flash("No file selected.", "warning")
        return redirect(url_for("files.file_list"))

    f = request.files["file"]
    if f.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("files.file_list"))

    if not _allowed_file(f.filename):
        flash("File type not allowed.", "danger")
        return redirect(url_for("files.file_list"))

    # Create a unique filename to avoid collisions / traversal
    original = secure_filename(f.filename)
    ext = original.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    f.save(os.path.join(upload_dir, stored_name))

    file_record = File(
        filename=stored_name,
        original_filename=original,
        owner_id=current_user.id,
    )
    db.session.add(file_record)
    db.session.commit()

    flash(f"'{original}' uploaded successfully!", "success")
    return redirect(url_for("files.file_list"))


@files.route("/download/<int:file_id>")
@login_required
def download(file_id):
    """Download a file (only if the current user owns it)."""
    file_record = db.get_or_404(File, file_id)
    if file_record.owner_id != current_user.id:
        abort(403)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        file_record.filename,
        as_attachment=True,
        download_name=file_record.original_filename,
    )


@files.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete(file_id):
    """Delete a file from disk and database."""
    file_record = db.get_or_404(File, file_id)
    if file_record.owner_id != current_user.id:
        abort(403)

    # Remove from disk
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_record.filename)
    if os.path.exists(path):
        os.remove(path)

    db.session.delete(file_record)
    db.session.commit()
    flash("File deleted.", "info")
    return redirect(url_for("files.file_list"))
