import os
import json
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, ForeignKey, JSON
from sqlalchemy.orm import relationship
import hashlib
import time

db = SQLAlchemy()

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SUBMISSIONS_DIR = os.path.join(DATA_DIR, 'submissions')
EVENTS_DIR = os.path.join(DATA_DIR, 'events')

# Association table
experience_requirement_link = Table(
    'experience_requirement_link',
    db.Model.metadata,
    db.Column('experience_id', db.Integer, db.ForeignKey('experiences.id'), primary_key=True),
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirements.id'), primary_key=True),
    db.Column('relevance_score', db.Float)
)

class Experience(db.Model):
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    experience_id = db.Column(db.String(16), unique=True)
    narrative_text = db.Column(db.Text, nullable=False)
    stakeholder_id = db.Column(db.Integer, db.ForeignKey('stakeholders.id'))
    # use generic JSON for portability (works with SQLite and Postgres)
    context_tags = db.Column(JSON)               # stores list of tags
    participants = db.Column(JSON)
    pain_points = db.Column(JSON)
    current_workaround = db.Column(db.Text)
    impact_severity = db.Column(db.String(50))
    emotional_indicators = db.Column(JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    
    stakeholder = db.relationship('Stakeholder', back_populates='experiences')
    requirements = db.relationship(
        'Requirement',
        secondary=experience_requirement_link,
        back_populates='experiences',
        overlaps="requirements,experiences"
    )
    analysis = db.relationship('ExperienceAnalysis', 
                             back_populates='experience',
                             uselist=False)

class Requirement(db.Model):
    __tablename__ = 'requirements'
    
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.String(16), unique=True)
    requirement_text = db.Column(db.Text, nullable=False)
    why_statement = db.Column(db.Text)
    priority = db.Column(db.String(50))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    
    experiences = db.relationship(
        'Experience',
        secondary=experience_requirement_link,
        back_populates='requirements',
        overlaps="requirements,experiences"
    )

os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
os.makedirs(EVENTS_DIR, exist_ok=True)


def _now_iso():
    """Return ISO format UTC timestamp with Z suffix"""
    return datetime.now(timezone.utc).isoformat()


# Relationship table for requirements dependencies
requirement_dependencies = Table(
    'requirement_dependencies', db.Model.metadata,
    db.Column('source_id', db.Integer, ForeignKey('requirement_submissions.id')),
    db.Column('target_id', db.Integer, ForeignKey('requirement_submissions.id'))
)

# Add association table for stakeholders and requirements
stakeholder_requirements = Table(
    'stakeholder_requirements', 
    db.Model.metadata,
    db.Column('stakeholder_id', db.Integer, ForeignKey('stakeholders.id')),
    db.Column('requirement_id', db.Integer, ForeignKey('requirement_submissions.id'))
)

class Stakeholder(db.Model):
    __tablename__ = 'stakeholders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100))
    department = db.Column(db.String(100))
    email = db.Column(db.String(255))
    requirements = relationship('RequirementSubmission', 
                              secondary='stakeholder_requirements',
                              back_populates='stakeholders')
    experiences = relationship('Experience', back_populates='stakeholder')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

class RequirementSubmission(db.Model):
    __tablename__ = 'requirement_submissions'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.String(16), unique=True, nullable=False, index=True)
    submission_text = db.Column(db.Text, nullable=False)
    sender_name = db.Column(db.String(255))
    sender_email = db.Column(db.String(255))
    source_type = db.Column(db.String(50), nullable=False, default='form')
    priority_hint = db.Column(db.String(50))
    linked_module = db.Column(db.String(100))
    privacy_mask = db.Column(db.Boolean, default=False)
    provenance = db.Column(JSON)
    status = db.Column(db.String(50), default='Submitted')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    dependencies = relationship('RequirementSubmission',
                              secondary=requirement_dependencies,
                              primaryjoin=id==requirement_dependencies.c.source_id,
                              secondaryjoin=id==requirement_dependencies.c.target_id,
                              backref='dependent_on')
    stakeholders = relationship('Stakeholder', 
                              secondary='stakeholder_requirements',
                              back_populates='requirements')
    priority = db.Column(db.String(50))
    impact_level = db.Column(db.String(50))
    verification_method = db.Column(db.String(100))

    def save(self):
        if not self.submission_id:
            base = (self.submission_text + (self.sender_email or '') + _now_iso())
            self.submission_id = hashlib.sha256(base.encode('utf-8')).hexdigest()[:16]
        
        for stakeholder in self.stakeholders:
            if stakeholder not in db.session:
                db.session.add(stakeholder)
        
        db.session.add(self)
        db.session.commit()
        return self

    def to_dict(self):
        return {
            'submission_id': self.submission_id,
            'submission_text': self.submission_text,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'source_type': self.source_type,
            'priority_hint': self.priority_hint,
            'linked_module': self.linked_module,
            'privacy_mask': self.privacy_mask,
            'provenance': self.provenance,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_recent_submissions(cls, limit=10):
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_by_status(cls, status):
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_by_text(cls, search_term):
        return cls.query.filter(cls.submission_text.ilike(f'%{search_term}%')).all()


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(16), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'payload': self.payload,
            'timestamp': self.created_at.isoformat()
        }

    @classmethod
    def get_recent_events(cls, limit=10):
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_type(cls, event_type):
        return cls.query.filter_by(event_type=event_type).order_by(cls.created_at.desc()).all()


def emit_event(event_type, payload):
    event_id = hashlib.sha256(
        (event_type + str(payload) + str(time.time())).encode('utf-8')
    ).hexdigest()[:16]
    
    event = Event(
        event_id=event_id,
        event_type=event_type,
        payload=payload
    )
    db.session.add(event)
    db.session.commit()
    return event.to_dict()


def find_duplicate_submission(text, window_seconds=300):
    """Find duplicate submissions within time window using database query."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
    try:
        # very simple similarity: recent submissions containing a substring
        dup = RequirementSubmission.query.filter(
            RequirementSubmission.submission_text.ilike(f'%{text[:50]}%'),
            RequirementSubmission.created_at >= cutoff
        ).order_by(RequirementSubmission.created_at.desc()).first()
        if dup:
            return dup.submission_id
    except Exception:
        pass
    return None

class ExperienceAnalysis(db.Model):
    __tablename__ = 'experience_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    experience_id = db.Column(db.Integer, db.ForeignKey('experiences.id'))
    extracted_goals = db.Column(JSON)
    identified_obstacles = db.Column(JSON)
    root_cause_hypothesis = db.Column(db.Text)
    # store lists of related experience ids as JSON array of ints for SQLite portability
    related_experiences = db.Column(JSON)
    sentiment_analysis = db.Column(JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationship back to Experience
    experience = db.relationship('Experience', back_populates='analysis')

class JobExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<JobExperience {self.title} at {self.company}>'
