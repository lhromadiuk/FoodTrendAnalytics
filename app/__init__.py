import os

from flask import Flask
from .config import Config
from .database import db
from .views import bp as main_bp
from .ingest import ingest_data

def create_app():
    pkg_dir = os.path.dirname(__file__)
    app = Flask(
        __name__,
        static_folder=os.path.join(pkg_dir, 'static'),
        static_url_path='/static',
        template_folder=os.path.join(pkg_dir, 'templates')
    )
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(main_bp)
    app.cli.add_command(ingest_data)

    # Create database tables immediately
    with app.app_context():
        db.create_all()

    return app

# Expose WSGI callable
app = create_app()
