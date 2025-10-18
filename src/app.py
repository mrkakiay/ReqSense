from flask import Flask, redirect
import os
from flask_migrate import Migrate
from src.models import db

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

    # Turn background jobs off by default during development / CI gating
    # Set USE_BG_JOBS=True in production/CI env when Redis + worker are available
    app.config['USE_BG_JOBS'] = os.environ.get('USE_BG_JOBS', '0') in ('1', 'true', 'True')

    db.init_app(app)
    Migrate(app, db)

    # register blueprints (if already present)
    try:
        from src.routes.experiences import experiences_bp
        from src.routes.stakeholders import stakeholders_bp
        app.register_blueprint(experiences_bp, url_prefix='/experiences')
        app.register_blueprint(stakeholders_bp, url_prefix='/stakeholders')
    except Exception:
        # allow app to start even if blueprints not ready yet
        pass

    @app.route('/')
    def index():
        return redirect('/experiences/')

    return app

# top-level app for flask CLI
app = create_app()
