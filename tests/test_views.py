from flask import url_for
from src.models import Stakeholder, RequirementSubmission, db
import pytest
from src.app import app

@pytest.fixture
def application():
    """Create application for testing"""
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    return app

@pytest.fixture
def client(application):
    """Create test client"""
    return application.test_client()

@pytest.fixture
def app_context(application):
    """Create application context"""
    with application.app_context():
        yield

@pytest.fixture
def test_data(app_context, db):
    """Create test data for traceability matrix"""
    # Create stakeholder
    stakeholder = Stakeholder(
        name="John Doe",
        role="Project Manager",
        department="Engineering"
    )
    db.session.add(stakeholder)
    
    # Create requirement
    req1 = RequirementSubmission(
        submission_text="First requirement",
        priority="High",
        status="In Progress"
    )
    req1.stakeholders.append(stakeholder)
    req1.save()
    
    yield {'stakeholder': stakeholder, 'requirement': req1}
    
    # Cleanup
    db.session.delete(req1)
    db.session.delete(stakeholder)
    db.session.commit()

@pytest.fixture
def complex_test_data(app_context, db):
    """Create complex test data for traceability matrix"""
    # Create stakeholders
    stakeholders = [
        Stakeholder(name="John Doe", role="Project Manager", department="Engineering"),
        Stakeholder(name="Jane Smith", role="Business Analyst", department="Business"),
        Stakeholder(name="Bob Wilson", role="Developer", department="Engineering")
    ]
    for s in stakeholders:
        s.save()
    
    # Create requirements with relationships
    reqs = [
        RequirementSubmission(
            submission_text="User authentication system",
            priority="High",
            status="In Progress",
            verification_method="System Test"
        ),
        RequirementSubmission(
            submission_text="Database backup functionality",
            priority="Medium",
            status="Approved",
            verification_method="Integration Test"
        ),
        RequirementSubmission(
            submission_text="Report generation module",
            priority="Low",
            status="Submitted",
            verification_method="Unit Test"
        )
    ]
    
    # Add stakeholder relationships and save
    reqs[0].stakeholders.extend([stakeholders[0], stakeholders[2]])
    reqs[0].save()
    
    reqs[1].stakeholders.append(stakeholders[1])
    reqs[1].save()
    
    reqs[2].stakeholders.extend(stakeholders)
    reqs[2].save()
    
    # Add dependencies
    reqs[2].dependencies.append(reqs[0])
    reqs[2].dependencies.append(reqs[1])
    reqs[2].save()
    
    yield {
        'stakeholders': stakeholders,
        'requirements': reqs
    }
    
    # Cleanup
    for r in reqs:
        db.session.delete(r)
    for s in stakeholders:
        db.session.delete(s)
    db.session.commit()

def test_traceability_matrix_view(client, app_context, test_data):
    """Test the traceability matrix view"""
    response = client.get(url_for('traceability_matrix'))
    assert response.status_code == 200
    assert b"Requirements Traceability Matrix" in response.data
    assert b"John Doe" in response.data

def test_traceability_matrix_complex(client, app_context, complex_test_data):
    """Test the traceability matrix view with complex relationships"""
    response = client.get(url_for('traceability_matrix'))
    assert response.status_code == 200
    
    content = response.data.decode('utf-8')
    
    # Check requirements presence
    assert "User authentication system" in content
    assert "Database backup functionality" in content
    assert "Report generation module" in content
    
    # Check stakeholders
    assert "John Doe" in content
    assert "Jane Smith" in content
    assert "Bob Wilson" in content
    
    # Check roles
    assert "Project Manager" in content
    assert "Business Analyst" in content
    assert "Developer" in content
    
    # Check status badges
    assert "bg-warning" in content  # For "In Progress"
    assert "bg-success" in content  # For "Approved"
    assert "bg-secondary" in content  # For "Submitted"
    
    # Check verification methods
    assert "System Test" in content
    assert "Integration Test" in content
    assert "Unit Test" in content
    
    # Check priorities
    assert "bg-high" in content
    assert "bg-medium" in content
    assert "bg-low" in content

def test_traceability_matrix_filtering(client, app_context, complex_test_data):
    """Test filtering capabilities in traceability matrix"""
    # Test filtering by priority
    response = client.get(url_for('traceability_matrix', priority='High'))
    content = response.data.decode('utf-8')
    assert "User authentication system" in content
    assert "Database backup functionality" not in content
    
    # Test filtering by status
    response = client.get(url_for('traceability_matrix', status='Approved'))
    content = response.data.decode('utf-8')
    assert "Database backup functionality" in content
    assert "User authentication system" not in content
    
    # Test filtering by stakeholder
    response = client.get(url_for('traceability_matrix', stakeholder='Jane Smith'))
    content = response.data.decode('utf-8')
    assert "Database backup functionality" in content
    assert "Report generation module" in content
    assert "User authentication system" not in content

def test_traceability_matrix_dependencies(client, app_context, complex_test_data):
    """Test dependency relationships in traceability matrix"""
    response = client.get(url_for('traceability_matrix'))
    content = response.data.decode('utf-8')
    
    reqs = complex_test_data['requirements']
    
    # Check that Report Generation shows dependencies
    assert reqs[0].submission_id in content  # Auth system ID
    assert reqs[1].submission_id in content  # Database backup ID
    
    # Check dependency badges
    assert f'href="#{reqs[0].submission_id}"' in content
    assert f'href="#{reqs[1].submission_id}"' in content