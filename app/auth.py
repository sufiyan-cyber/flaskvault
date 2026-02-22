"""Authentication blueprint — register, login, logout."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Log an existing user in."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()

        if not user:
            flash("That email does not exist, please try again.", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")

        existing = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()

        if existing:
            flash("You've already signed up with that email — log in instead!", "warning")
            return redirect(url_for("auth.login"))

        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(
                password, method="pbkdf2:sha256", salt_length=8
            ),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Account created — welcome!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("register.html")


@auth.route("/logout")
@login_required
def logout():
    """Log the current user out."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
