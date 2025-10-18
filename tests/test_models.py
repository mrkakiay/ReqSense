from datetime import datetime, timezone, timedelta
from src.models import RequirementSubmission, Event, find_duplicate_submission, db

def test_requirement_submission_creation(db):
    submission = RequirementSubmission(
        submission_text="Test requirement",
        sender_name="Test User",
        sender_email="test@example.com"
    )
    submission.save()
    
    assert submission.submission_id is not None
    assert submission.created_at is not None
    
    fetched = RequirementSubmission.query.filter_by(submission_id=submission.submission_id).first()
    assert fetched is not None
    assert fetched.submission_text == "Test requirement"

def test_event_creation(db):
    event = Event(
        event_id="test123",
        event_type="TestEvent",
        payload={"test": "data"}
    )
    db.session.add(event)
    db.session.commit()
    
    fetched = Event.query.filter_by(event_id="test123").first()
    assert fetched is not None
    assert fetched.payload == {"test": "data"}

def test_find_duplicate_submission(db):
    submission1 = RequirementSubmission(
        submission_text="Duplicate text",
        sender_name="Test User"
    )
    submission1.save()
    
    duplicate_id = find_duplicate_submission("Duplicate text")
    assert duplicate_id == submission1.submission_id

def test_submission_search(db):
    """Test submission search functionality."""
    submissions = [
        RequirementSubmission(submission_text="Test requirement 1", sender_name="User 1"),
        RequirementSubmission(submission_text="Different text 2", sender_name="User 2"),
        RequirementSubmission(submission_text="Test requirement 3", sender_name="User 3")
    ]
    for s in submissions:
        s.save()
    
    results = RequirementSubmission.search_by_text("Test requirement")
    assert len(results) == 2
    
def test_submission_status_filtering(db):
    """Test filtering submissions by status."""
    s1 = RequirementSubmission(submission_text="Text 1", status="Submitted")
    s2 = RequirementSubmission(submission_text="Text 2", status="Approved")
    s3 = RequirementSubmission(submission_text="Text 3", status="Approved")
    for s in [s1, s2, s3]:
        s.save()
    
    approved = RequirementSubmission.get_by_status("Approved")
    assert len(approved) == 2

def test_event_type_filtering(db):
    """Test filtering events by type."""
    events = [
        Event(event_id="e1", event_type="TypeA", payload={"data": 1}),
        Event(event_id="e2", event_type="TypeB", payload={"data": 2}),
        Event(event_id="e3", event_type="TypeA", payload={"data": 3})
    ]
    for e in events:
        db.session.add(e)
    db.session.commit()
    
    type_a_events = Event.get_by_type("TypeA")
    assert len(type_a_events) == 2