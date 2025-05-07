import os

from flask import Flask, render_template

from .config import Config
from .database import db
from .embedding import tokenize_recipe
from .ingest import cli_ingest_data, cli_train_word2vec
from .views import bp as main_bp


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
    app.cli.add_command(cli_ingest_data)
    app.cli.add_command(cli_train_word2vec)
    # use Alembic for migration later on
    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app


app = create_app()
