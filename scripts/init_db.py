import os
import sys
from flask import Flask
from sqlalchemy import text

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(project_root))

from ReqSense.src.models import db, RequirementSubmission, Stakeholder
from ReqSense.src.config import Config

def init_database():
    try:
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'postgresql://reqsense_user:reqsense_pass@localhost:5432/reqsense'
        )
        app.config.from_object(Config)
        db.init_app(app)
        
        with app.app_context():
            # Test connection
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Create tables
            db.create_all()
            print("✓ Database tables created successfully!")
            
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)