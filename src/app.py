from flask import Flask, redirect
import os
from flask_migrate import Migrate
from src.models import db

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

    db.init_app(app)
    Migrate(app, db)

    # register blueprints
    from src.routes.experiences import experiences_bp
    from src.routes.stakeholders import stakeholders_bp
    app.register_blueprint(experiences_bp, url_prefix='/experiences')
    app.register_blueprint(stakeholders_bp, url_prefix='/stakeholders')

    @app.route('/')
    def index():
        return redirect('/experiences/')

    return app

# top-level app for flask CLI
app = create_app()
