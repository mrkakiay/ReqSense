from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.models import db, Stakeholder

stakeholders_bp = Blueprint('stakeholders', __name__, template_folder='../templates/stakeholders')

@stakeholders_bp.route('/', methods=['GET'])
def overview():
    """
    Stakeholders overview with simple Mendelow quadrant calculation.
    Assumes optional numeric fields 'importance' and 'influence' may exist on model
    (0-10). If not present, shows 'n/a'.
    """
    stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
    return render_template('stakeholders/overview.html', stakeholders=stakeholders)

@stakeholders_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = request.form
        s = Stakeholder(
            name=data.get('name','').strip(),
            role=data.get('role') or None,
            department=data.get('department') or None,
            email=data.get('email') or None,
            type=data.get('type') or None,
            importance=int(data.get('importance')) if data.get('importance') else None,
            influence=int(data.get('influence')) if data.get('influence') else None,
            notes=data.get('notes') or None
        )
        db.session.add(s)
        db.session.commit()
        flash('Stakeholder created.', 'success')
        return redirect(url_for('stakeholders.overview'))
    return render_template('stakeholders/form.html', stakeholder=None)

@stakeholders_bp.route('/<int:stakeholder_id>/edit', methods=['GET', 'POST'])
def edit(stakeholder_id):
    s = Stakeholder.query.get_or_404(stakeholder_id)
    if request.method == 'POST':
        data = request.form
        s.name = data.get('name','').strip()
        s.role = data.get('role') or None
        s.department = data.get('department') or None
        s.email = data.get('email') or None
        s.type = data.get('type') or None
        s.importance = int(data.get('importance')) if data.get('importance') else None
        s.influence = int(data.get('influence')) if data.get('influence') else None
        s.notes = data.get('notes') or None
        db.session.commit()
        flash('Stakeholder updated.', 'success')
        return redirect(url_for('stakeholders.overview'))
    return render_template('stakeholders/form.html', stakeholder=s)

@stakeholders_bp.route('/<int:stakeholder_id>/delete', methods=['POST'])
def delete(stakeholder_id):
    s = Stakeholder.query.get_or_404(stakeholder_id)
    db.session.delete(s)
    db.session.commit()
    flash('Stakeholder deleted.', 'info')
    return redirect(url_for('stakeholders.overview'))

@stakeholders_bp.route('/<int:stakeholder_id>', methods=['GET'])
def view(stakeholder_id):
    s = Stakeholder.query.get_or_404(stakeholder_id)
    return render_template('stakeholders/view.html', stakeholder=s)