from flask import Flask
from src.models import db, RequirementSubmission, Event
from src.config import Config
from sqlalchemy import text, select
from datetime import datetime, timezone
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_database():
    try:
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)
        
        with app.app_context():
            # Test 1: Database Connection
            result = db.session.execute(text('SELECT 1')).scalar()
            assert result == 1, "Database connection failed"
            print("✓ Database connection successful")
            
            # Test 2: Create Submission
            test_submission = RequirementSubmission(
                submission_text="Test requirement",
                sender_name="Test User",
                sender_email="test@example.com",
                priority_hint="High",
                linked_module="Testing"
            )
            test_submission.save()
            assert test_submission.submission_id is not None, "Submission ID not generated"
            assert test_submission.created_at is not None, "Creation timestamp not set"
            print("✓ Submission creation successful")
            
            # Test 3: Create Event
            event_payload = {"test": "data", "timestamp": datetime.now(timezone.utc).isoformat()}
            test_event = Event(
                event_id="test123",
                event_type="TestEvent",
                payload=event_payload
            )
            db.session.add(test_event)
            db.session.commit()
            assert test_event.id is not None, "Event ID not generated"
            print("✓ Event creation successful")
            
            # Test 4: Query Data
            stmt = select(RequirementSubmission)
            submissions = db.session.scalars(stmt).all()
            stmt = select(Event)
            events = db.session.scalars(stmt).all()
            assert len(submissions) > 0, "No submissions found"
            assert len(events) > 0, "No events found"
            print(f"✓ Found {len(submissions)} submissions and {len(events)} events")
            
            # Test 5: JSONB Operations
            stmt = select(Event).where(Event.event_id == "test123")
            retrieved_event = db.session.scalar(stmt)
            assert retrieved_event.payload == event_payload, "JSONB data mismatch"
            print("✓ JSONB operations successful")
            
            # Cleanup
            db.session.delete(test_submission)
            db.session.delete(test_event)
            db.session.commit()
            
            # Verify cleanup
            stmt = select(RequirementSubmission).where(RequirementSubmission.id == test_submission.id)
            assert db.session.scalar(stmt) is None, "Submission not deleted"
            stmt = select(Event).where(Event.id == test_event.id)
            assert db.session.scalar(stmt) is None, "Event not deleted"
            print("✓ Cleanup successful")
            
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = test_database()
    sys.exit(0 if success else 1)