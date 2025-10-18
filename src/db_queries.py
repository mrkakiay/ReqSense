from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, RequirementSubmission, Event, Experience

def get_submission_statistics():
    """Get submission statistics for the dashboard."""
    return {
        'total_submissions': RequirementSubmission.query.count(),
        'submissions_today': RequirementSubmission.query.filter(
            RequirementSubmission.created_at >= datetime.utcnow().date()
        ).count(),
        'by_status': db.session.query(
            RequirementSubmission.status,
            func.count(RequirementSubmission.id)
        ).group_by(RequirementSubmission.status).all()
    }

def get_recent_activity(days=7):
    """Get recent submission and event activity."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    submissions = RequirementSubmission.query.filter(
        RequirementSubmission.created_at >= cutoff
    ).order_by(RequirementSubmission.created_at.desc()).all()
    
    events = Event.query.filter(
        Event.created_at >= cutoff
    ).order_by(Event.created_at.desc()).all()
    
    return {
        'submissions': [s.to_dict() for s in submissions],
        'events': [e.to_dict() for e in events]
    }

def search_submissions(query, include_archived=False):
    """Search submissions with various filters."""
    base_query = RequirementSubmission.query
    
    if not include_archived:
        base_query = base_query.filter(RequirementSubmission.status != 'Archived')
    
    return base_query.filter(
        RequirementSubmission.submission_text.ilike(f'%{query}%')
    ).order_by(RequirementSubmission.created_at.desc()).all()

def get_experiences():
    try:
        return Experience.query.all()
    except Exception as e:
        return []

def create_experience(data):
    try:
        experience = Experience(**data)
        db.session.add(experience)
        db.session.commit()
        return experience
    except Exception as e:
        db.session.rollback()
        raise e