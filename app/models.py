"""Database models for the application."""

from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class User(db.Model, UserMixin):
    """Registered user."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    # One-to-many: a user owns many files
    files = relationship("File", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class File(db.Model):
    """Uploaded file metadata."""
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(300), nullable=False)        # stored name on disk
    original_filename: Mapped[str] = mapped_column(String(300), nullable=False)  # name the user sees
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="files")

    def __repr__(self):
        return f"<File {self.original_filename}>"
