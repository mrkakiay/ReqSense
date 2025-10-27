from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.models import db, Experience, Stakeholder

experiences_bp = Blueprint('experiences', __name__, template_folder='../templates/experiences')

@experiences_bp.route('/', methods=['GET'])
def overview():
    experiences = Experience.query.order_by(Experience.created_at.desc()).all()
    return render_template('experiences/overview.html', experiences=experiences)

@experiences_bp.route('/submit', methods=['GET', 'POST'])
def submit_experience():
    # GET: show form with stakeholders list
    if request.method == 'GET':
        stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
        return render_template('experiences/submit_experience.html', stakeholders=stakeholders)

    # POST: create a new Experience (minimal fields)
    data = request.form
    narrative = data.get('narrative_text', '').strip()
    stakeholder_id = data.get('stakeholder_id') or None
    context_tags_raw = data.get('context_tags') or ''
    context_tags = [t.strip() for t in context_tags_raw.split(',') if t.strip()] if context_tags_raw else None
    current_workaround = data.get('current_workaround') or None
    impact_severity = data.get('impact_severity') or None

    if not narrative:
        flash('Narrative is required.', 'error')
        stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
        return render_template('experiences/submit_experience.html', stakeholders=stakeholders)

    exp = Experience(
        narrative_text=narrative,
        stakeholder_id=int(stakeholder_id) if stakeholder_id else None,
        context_tags=context_tags,
        current_workaround=current_workaround,
        impact_severity=impact_severity
    )
    db.session.add(exp)
    db.session.commit()
    flash('Experience submitted.', 'success')
    return redirect(url_for('experiences.overview'))

@experiences_bp.route('/traceability', methods=['GET'])
def traceability():
    """
    Minimal traceability view so the nav link in base.html resolves.
    Extend this page later with real traceability visuals.
    """
    # lightweight placeholder data (replace with real queries later)
    experiences = Experience.query.order_by(Experience.created_at.desc()).limit(10).all()
    return render_template('experiences/traceability.html', experiences=experiences)

@experiences_bp.route('/<int:experience_id>/edit', methods=['GET', 'POST'])
def edit_experience(experience_id):
    exp = Experience.query.get_or_404(experience_id)
    if request.method == 'POST':
        data = request.form
        narrative = data.get('narrative_text','').strip()
        if not narrative:
            flash('Narrative required.', 'error')
            stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
            return render_template('experiences/edit_experience.html', experience=exp, stakeholders=stakeholders)
        exp.narrative_text = narrative
        exp.current_workaround = data.get('current_workaround') or None
        exp.impact_severity = data.get('impact_severity') or None
        exp.stakeholder_id = int(data.get('stakeholder_id')) if data.get('stakeholder_id') else None
        ctx = data.get('context_tags') or ''
        exp.context_tags = [t.strip() for t in ctx.split(',') if t.strip()] if ctx else None
        db.session.commit()
        flash('Experience updated.', 'success')
        return redirect(url_for('experiences.overview'))

    stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
    return render_template('experiences/edit_experience.html', experience=exp, stakeholders=stakeholders)