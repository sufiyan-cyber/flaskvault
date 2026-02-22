"""Flask extensions instantiated here (without binding to an app yet).

They are initialised inside create_app() via init_app().
This avoids circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Where to redirect unauthenticated users
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
