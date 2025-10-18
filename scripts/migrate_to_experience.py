import os
import sys
from flask import Flask
from sqlalchemy import text

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import db, Experience, ExperienceAnalysis, Requirement
from src.config import Config

def migrate_to_experience():
    try:
        app = Flask(__name__)
        
        # Ensure PostgreSQL connection
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'postgresql://reqsense_user:reqsense_pass@localhost:5432/reqsense'
        )
        app.config.from_object(Config)
        db.init_app(app)
        
        with app.app_context():
            # Test connection using SQLAlchemy text()
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Create new tables
            db.create_all()
            print("✓ Created new tables")
            
            # Show tables being created
            inspector = db.inspect(db.engine)
            print("\nNew tables:")
            for table in inspector.get_table_names():
                print(f"  - {table}")
            
            # Migrate existing submissions if any
            if 'requirement_submissions' in inspector.get_table_names():
                result = db.session.execute(
                    text('SELECT * FROM requirement_submissions')
                )
                migrated = 0
                for row in result:
                    experience = Experience(
                        narrative_text=row.submission_text,
                        stakeholder_id=row.sender_id if hasattr(row, 'sender_id') else None,
                        impact_severity='Medium',  # Default value
                        context_tags=[row.source_type] if hasattr(row, 'source_type') else []
                    )
                    db.session.add(experience)
                    migrated += 1
                
                db.session.commit()
                print(f"✓ Migrated {migrated} submissions to experiences")
            else:
                print("No existing submissions to migrate")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = migrate_to_experience()
    sys.exit(0 if success else 1)