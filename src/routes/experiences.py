from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import json
from src.models import Experience, db, RequirementSuggestion
from ..services.experience_analyzer import ExperienceAnalyzer
import os
from rq import Queue
from redis import Redis

experiences_bp = Blueprint('experiences', __name__, template_folder='../templates/experiences')

@experiences_bp.route('/')
def overview():
    """List view with experience-specific metadata."""
    experiences = Experience.query.order_by(Experience.created_at.desc()).all()
    return render_template('experiences/list.html', experiences=experiences)

@experiences_bp.route('/traceability')
def traceability():
    """Traceability & Requirements matrix (separate page)."""
    experiences = Experience.query.order_by(Experience.created_at.desc()).all()
    return render_template('experiences/traceability.html', experiences=experiences)

@experiences_bp.route('/submit-experience', methods=['GET', 'POST'])
def submit_experience():
    if request.method == 'POST':
        narrative_text = request.form.get('narrative_text')
        current_workaround = request.form.get('current_workaround')
        impact_severity = request.form.get('impact_severity')
        context_tags = request.form.get('context_tags')

        if not narrative_text or not impact_severity:
            flash('Please fill in narrative text and impact severity', 'error')
            return redirect(request.url)

        experience = Experience(
            narrative_text=narrative_text,
            current_workaround=current_workaround,
            impact_severity=impact_severity,
            context_tags=context_tags.split(',') if context_tags else []
        )

        db.session.add(experience)
        db.session.commit()

        flash('Experience submitted successfully', 'success')
        return redirect(url_for('experiences.overview'))

    return render_template('experiences/submit_experience.html')

@experiences_bp.route('/<int:experience_id>/edit', methods=['GET', 'POST'])
def edit_experience(experience_id):
    """Edit an existing experience."""
    experience = Experience.query.get_or_404(experience_id)
    
    if request.method == 'POST':
        experience.narrative_text = request.form.get('narrative_text', experience.narrative_text)
        experience.current_workaround = request.form.get('current_workaround', experience.current_workaround)
        experience.impact_severity = request.form.get('impact_severity', experience.impact_severity)
        tags = request.form.get('context_tags')
        experience.context_tags = tags.split(',') if tags else experience.context_tags
        
        db.session.commit()
        flash('Experience updated successfully', 'success')
        return redirect(url_for('experiences.overview'))
    
    return render_template('experiences/edit.html', experience=experience)

@experiences_bp.route('/patterns')
def patterns():
    """Show experience patterns."""
    return render_template('experiences/patterns.html')

@experiences_bp.route('/<int:experience_id>/generate-requirement')
def generate_requirement(experience_id):
    """Generate an AI-suggested requirement from an experience."""
    experience = Experience.query.get_or_404(experience_id)
    
    # Use the ExperienceAnalyzer to generate a requirement
    analyzer = ExperienceAnalyzer()
    generated_requirement = analyzer.generate_requirement(experience)
    
    return render_template('experiences/generated_requirement.html', 
                         experience=experience, 
                         generated_requirement=generated_requirement)

@experiences_bp.route('/<int:experience_id>/enqueue-generate', methods=['POST'])
def enqueue_generate(experience_id):
    """Enqueue generation job — guarded by app config.
       If background jobs are disabled, create a 'manual' placeholder suggestion and return.
    """
    # Do not attempt to use Redis/RQ unless enabled explicitly
    if not current_app.config.get('USE_BG_JOBS', False):
        # create a placeholder suggestion record (for later processing)
        sug = RequirementSuggestion(
            experience_id=experience_id,
            status='queued_manually',
            params=(json.loads(request.form.get('params')) if request.form.get('params') else {})
        )
        db.session.add(sug)
        db.session.commit()
        flash('Background generation is disabled. Suggestion queued for manual/CI processing.', 'info')
        return redirect(url_for('experiences.overview'))

    # existing enqueue logic (kept for future) — not executed unless USE_BG_JOBS True
    params = {}
    if request.form.get('params'):
        try:
            params = json.loads(request.form.get('params'))
        except Exception:
            params = {}

    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    redis_conn = Redis.from_url(redis_url)
    q = Queue('default', connection=redis_conn)
    job = q.enqueue('src.workers.generate_requirement.generate_requirement_job', experience_id, params)

    sug = RequirementSuggestion(experience_id=experience_id, status='pending', params=params)
    db.session.add(sug); db.session.commit()
    flash('Generation job enqueued.', 'success')
    return redirect(url_for('experiences.overview'))