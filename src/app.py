from flask import Flask, redirect
import os
from flask_migrate import Migrate
from src.models import db  # use the shared SQLAlchemy instance

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI'
    ) or os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

    # initialize DB and migrations with the shared db instance
    db.init_app(app)
    Migrate(app, db)

    # register blueprints after db.init_app to avoid "app not registered" errors
    from src.routes.experiences import experiences_bp
    app.register_blueprint(experiences_bp, url_prefix='/experiences')

    @app.route('/')
    def index():
        return redirect('/experiences/')

    return app

# top-level app for flask CLI
app = create_app()
