from flask import Blueprint

# Create blueprint with template folder
experiences_bp = Blueprint('experiences', __name__, 
                         template_folder='templates')

# Import views after blueprint creation to avoid circular imports
from . import views
from .views import experiences_bp

__all__ = ['experiences_bp']