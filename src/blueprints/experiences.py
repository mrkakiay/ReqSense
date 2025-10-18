from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.models import db, Experience, ExperienceAnalysis
from sqlalchemy import select
from datetime import datetime, timezone

experiences_bp = Blueprint('experiences', __name__)

@experiences_bp.route('/')
def overview():
    experiences = Experience.query.order_by(Experience.created_at.desc()).all()
    return render_template('experiences/overview.html', experiences=experiences)

@experiences_bp.route('/submit-experience', methods=['GET', 'POST'])
def submit_experience():
    if request.method == 'POST':
        experience = Experience(
            narrative_text=request.form['narrative_text'],
            current_workaround=request.form['current_workaround'],
            impact_severity=request.form['impact_severity'],
            context_tags=request.form['context_tags'].split(',') if request.form['context_tags'] else []
        )
        
        db.session.add(experience)
        db.session.commit()
        
        # Create initial analysis
        analysis = ExperienceAnalysis(
            experience_id=experience.id,
            extracted_goals={},
            identified_obstacles={},
            sentiment_analysis={}
        )
        db.session.add(analysis)
        db.session.commit()
        
        flash('Experience submitted successfully', 'success')
        return redirect(url_for('experiences.overview'))
        
    return render_template('experiences/submit.html')
    
@experiences_bp.route('/<int:experience_id>/edit', methods=['GET', 'POST'])
def edit_experience(experience_id):
    """Edit an existing experience."""
    experience = Experience.query.get_or_404(experience_id)
    if request.method == 'POST':
        try:
            experience.narrative_text = request.form.get('narrative_text', experience.narrative_text)
            experience.current_workaround = request.form.get('current_workaround', experience.current_workaround)
            experience.impact_severity = request.form.get('impact_severity', experience.impact_severity)
            tags = request.form.get('context_tags')
            experience.context_tags = tags.split(',') if tags else experience.context_tags
            experience.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            flash('Experience updated successfully', 'success')
            return redirect(url_for('experiences.overview'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating experience: {e}', 'danger')
    return render_template('experiences/edit.html', experience=experience)