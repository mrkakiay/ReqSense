from .experiences import experiences_bp
from flask import Blueprint

stakeholders_bp = Blueprint('stakeholders', __name__)

# Add your routes here

__all__ = ['experiences_bp', 'stakeholders_bp']