# commands.py
import click 
from flask.cli import with_appcontext
from app.db import db
from app.models.user import User, UserType

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize database tables."""
    try:
        db.create_all()
        click.echo('Initialized database.')
    except Exception as e:
        click.echo(f'Error initializing database: {e}')

@click.command('add-test-user')
@with_appcontext
def add_test_user():
    """Add a test user."""
    try:
        user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            user_type=UserType.STUDENT
        )
        db.session.add(user)
        db.session.commit()
        click.echo('Added test user.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error adding test user: {e}')