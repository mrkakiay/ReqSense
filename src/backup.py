import subprocess
import os
from datetime import datetime, timezone
import click

BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup(database_url):
    """Create a PostgreSQL backup."""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'reqsense_backup_{timestamp}.sql')
    
    # Parse database URL
    db_url = database_url.replace('postgresql://', '')
    user_pass, host_db = db_url.split('@')
    user, password = user_pass.split(':')
    host, db = host_db.split('/')
    
    # Set environment for pg_dump
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        subprocess.run([
            'pg_dump',
            '-h', host,
            '-U', user,
            '-d', db,
            '-f', backup_file
        ], env=env, check=True)
        click.echo(f"Backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        click.echo(f"Backup failed: {e}")
        return None

def restore_backup(database_url, backup_file):
    """Restore from a PostgreSQL backup."""
    if not os.path.exists(backup_file):
        click.echo(f"Backup file not found: {backup_file}")
        return False
    
    # Parse database URL
    db_url = database_url.replace('postgresql://', '')
    user_pass, host_db = db_url.split('@')
    user, password = user_pass.split(':')
    host, db = host_db.split('/')
    
    # Set environment for psql
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        subprocess.run([
            'psql',
            '-h', host,
            '-U', user,
            '-d', db,
            '-f', backup_file
        ], env=env, check=True)
        click.echo(f"Restore completed from: {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        click.echo(f"Restore failed: {e}")
        return False