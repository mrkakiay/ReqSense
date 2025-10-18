from flask import Blueprint, render_template

stakeholders_bp = Blueprint('stakeholders', __name__)

@stakeholders_bp.route('/stakeholders')
def stakeholders():
    return render_template('stakeholders.html')