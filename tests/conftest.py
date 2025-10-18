import pytest
from src.app import app as flask_app
from src.models import db
from sqlalchemy import text, event
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    # Database URL with required parameters
    db_url = 'postgresql+psycopg2://reqsense_user:reqsense_pass@localhost:5432/reqsense_test'
    
    # Configure Flask app
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'isolation_level': 'REPEATABLE READ',
            'pool_pre_ping': True,
            'echo': True
        }
    })
    
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner for Flask commands."""
    return app.test_cli_runner()

@pytest.fixture(scope='session')
def app_context(app):
    with app.app_context():
        try:
            # Test PostgreSQL connection
            result = db.session.execute(text('SELECT 1')).scalar()
            print("✓ Connected to PostgreSQL database")
            
            # Clean up any existing tables
            db.drop_all()
            # Create fresh tables
            db.create_all()
            print("✓ Created test database tables")
            
            yield
            
        except Exception as e:
            print(f"Error setting up test database: {str(e)}")
            raise
        finally:
            db.session.remove()

@pytest.fixture
def db_session(app_context):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create session factory bound to this connection
    session_factory = sessionmaker(bind=connection)
    
    # Create a scoped session
    Session = scoped_session(session_factory)
    session = Session()
    
    # Begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()
    
    # If the session ends, reopen a new SAVEPOINT
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    event.listen(Session, 'after_transaction_end', restart_savepoint)
    
    yield session
    
    # Cleanup
    Session.remove()
    transaction.rollback()
    connection.close()