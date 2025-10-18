import click
from flask.cli import with_appcontext
from .models import db, RequirementSubmission, Event
from datetime import datetime, timezone, timedelta

@click.group()
def db_cli():
    """Database management commands."""
    pass

@db_cli.command()
@with_appcontext
def stats():
    """Show database statistics."""
    submissions_count = RequirementSubmission.query.count()
    events_count = Event.query.count()
    latest_submission = RequirementSubmission.query.order_by(RequirementSubmission.created_at.desc()).first()
    
    click.echo(f"Total Submissions: {submissions_count}")
    click.echo(f"Total Events: {events_count}")
    if latest_submission:
        click.echo(f"Latest Submission: {latest_submission.created_at.isoformat()}")

@db_cli.command()
@click.option('--days', default=30, help='Number of days to keep')
@with_appcontext
def cleanup_old_events(days):
    """Remove events older than specified days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    deleted = Event.query.filter(Event.created_at < cutoff).delete()
    db.session.commit()
    click.echo(f"Deleted {deleted} old events")

@db_cli.command()
@click.argument('search_text')
@with_appcontext
def search_submissions(search_text):
    """Search submissions by text."""
    results = RequirementSubmission.search_by_text(search_text)
    for r in results:
        click.echo(f"ID: {r.submission_id} - {r.submission_text[:50]}...")