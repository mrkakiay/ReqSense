from flask import Blueprint, render_template
from src.models import Stakeholder

stakeholders_bp = Blueprint('stakeholders', __name__, template_folder='../templates/stakeholders')

@stakeholders_bp.route('/')
def overview():
    """
    Stakeholders overview with simple Mendelow quadrant calculation.
    Assumes optional numeric fields 'importance' and 'influence' may exist on model
    (0-10). If not present, shows 'n/a'.
    """
    stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
    return render_template('stakeholders/overview.html', stakeholders=stakeholders)