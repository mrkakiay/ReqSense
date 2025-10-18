import pytest
from src.models import Experience, ExperienceAnalysis
from datetime import datetime, timezone

def test_submit_experience(client, app_context, db_session):
    """Test submitting a new experience through the form."""
    response = client.post('/submit-experience', data={
        'narrative_text': 'Test experience narrative',
        'current_workaround': 'Current test workaround',
        'impact_severity': 'High',
        'context_tags': 'test,experience',
        'participants': '{"role": "user", "department": "IT"}',
        'pain_points': '{"issue": "performance", "frequency": "daily"}'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Experience submitted successfully' in response.data
    
    experience = db_session.query(Experience).first()
    assert experience is not None
    assert experience.narrative_text == 'Test experience narrative'

def test_experience_view(client, app_context):
    """Test viewing the experience submission form."""
    response = client.get('/submit-experience')
    assert response.status_code == 200
    assert b'Share Your Experience' in response.data