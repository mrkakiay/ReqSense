# ReqSense Database Features Documentation

## Database Setup

1. Install PostgreSQL dependencies:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Create PostgreSQL database and user:
```bash
sudo -u postgres psql

CREATE DATABASE reqsense;
CREATE USER reqsense_user WITH PASSWORD 'reqsense_pass';
GRANT ALL PRIVILEGES ON DATABASE reqsense TO reqsense_user;
\c reqsense
GRANT ALL ON SCHEMA public TO reqsense_user;
ALTER USER reqsense_user CREATEDB;  # Needed for testing
\q
```

3. Create a database initialization script:
````python
# filepath: /home/optimus/project_starter/ReqSense/scripts/init_db.py
from flask import Flask
from src.models import db
from src.config import Config

def init_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_database()
`````

## Database Management Commands

The following CLI commands help manage the ReqSense database:

```bash
# Show database statistics
flask stats

# Clean up old events (default 30 days)
flask cleanup-old-events --days 30

# Search submissions
flask search-submissions "search text"
```

## Health Check Endpoints

Two health check endpoints are available:

1. Basic Health Check (`/health`)
   ```bash
   curl http://localhost:5000/health
   ```
   Returns:
   ```json
   {
     "status": "healthy",
     "stats": {
       "database_connected": true,
       "submissions_count": 42,
       "events_count": 156,
       "timestamp": "2025-10-14T10:30:00Z"
     }
   }
   ```

2. Detailed Health Check (`/health/detailed`)
   ```bash
   curl http://localhost:5000/health/detailed
   ```
   Returns:
   ```json
   {
     "status": "healthy",
     "stats": {
       "database_connected": true,
       "total_submissions": 42,
       "submissions_24h": 5,
       "events_24h": 15,
       "submission_statuses": [
         ["Submitted", 20],
         ["Approved", 15],
         ["Rejected", 7]
       ]
     }
   }
   ```

## Database Backup and Restore

### Creating Backups

1. Using the script:
   ```bash
   ./ReqSense/scripts/backup.sh
   ```
   This creates a timestamped backup in `ReqSense/backups/`.

2. Manual backup:
   ```python
   from src.backup import create_backup
   backup_file = create_backup("postgresql://reqsense_user:reqsense_pass@localhost:5432/reqsense")
   ```

### Restoring from Backup

```python
from src.backup import restore_backup
restore_backup(
    "postgresql://reqsense_user:reqsense_pass@localhost:5432/reqsense",
    "/path/to/backup/reqsense_backup_20251014_103000.sql"
)
```

## Development Setup

1. Set environment variables:
   ```bash
   export FLASK_APP=ReqSense/src/app.py
   export FLASK_ENV=development
   export DATABASE_URL="postgresql://reqsense_user:reqsense_pass@localhost:5432/reqsense"
   ```

2. Start the application:
   ```bash
   flask run
   ```

3. Run the tests:
   ```bash
   pytest ReqSense/tests/ -v
   ```

## Automated Tasks

Add these to your crontab for automation:

```bash
# Daily backup at 2 AM
0 2 * * * /home/optimus/project_starter/ReqSense/scripts/backup.sh

# Clean old events weekly
0 3 * * 0 cd /home/optimus/project_starter && flask cleanup-old-events --days 30
```

## Database Monitoring

To monitor database health in production:

1. Set up monitoring endpoint:
   ```bash
   # Using curl in a monitoring script
   curl -f http://localhost:5000/health || notify_admin "Database health check failed"
   ```

2. Query submission statistics:
   ```python
   from src.models import RequirementSubmission
   
   # Get recent submissions
   recent = RequirementSubmission.get_recent_submissions(limit=10)
   
   # Get submissions by status
   approved = RequirementSubmission.get_by_status("Approved")
   ```

## Adding New Database Features

To add new database functionality:

1. Update models:
   ```python
   # Add new fields or tables to src/models.py
   class RequirementSubmission(db.Model):
       # Add new fields here
       new_field = db.Column(db.String(50))
   ```

2. Create tables:
   ```python
   with app.app_context():
       db.create_all()
   ```

3. Update tests:
   ```bash
   pytest ReqSense/tests/test_models.py -v
   ```