from __future__ import annotations

from flask import Flask

from .config import AppConfig, STATIC_DIR
from .routes.admin import admin_bp
from .routes.binlookup import binlookup_bp
from .routes.commands import commands_bp
from .routes.public import public_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/assets", template_folder="../templates")
    app.config["SECRET_KEY"] = AppConfig.secret_key

    app.register_blueprint(public_bp)
    app.register_blueprint(commands_bp)
    app.register_blueprint(binlookup_bp)
    app.register_blueprint(admin_bp)

    return app
