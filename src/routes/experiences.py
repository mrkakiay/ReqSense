from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.models import Experience, db
from ..services.experience_analyzer import ExperienceAnalyzer

experiences_bp = Blueprint('experiences', __name__, template_folder='../templates/experiences')

@experiences_bp.route('/')
def overview():
    """Display all experiences."""
    experiences = Experience.query.order_by(Experience.created_at.desc()).all()
    return render_template('experiences/overview.html', experiences=experiences)

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