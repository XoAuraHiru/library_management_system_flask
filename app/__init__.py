# app/__init__.py
from pathlib import Path
from flask import Flask
from typing import Optional, Type
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from dotenv import load_dotenv
from config import Config
from .db import db, migrate

# Load environment variables
load_dotenv()

def create_app(config_class: Optional[Type[Config]] = None) -> Flask:
    """Create and configure the Flask application.
    
    This factory function sets up the Flask app with all necessary configurations,
    database connections, logging, blueprints, and template utilities.
    
    Args:
        config_class: Optional configuration class, defaults to Config if None
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = Config
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create required directories
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    # Configure logging
    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            'logs/library.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Library Management System startup')
    
    # Add template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format a datetime object for display in templates.
        
        Args:
            value: The datetime object to format
            format: The strftime format string to use
            
        Returns:
            Formatted datetime string or empty string if value is None
        """
        if value is None:
            return ""
        return value.strftime(format)
    
    # Add context processors for template utilities
    @app.context_processor
    def utility_processor():
        """Add utility functions and variables to template context.
        
        Returns:
            Dictionary of utilities available in templates
        """
        return {
            'now': datetime.utcnow(),
            'format_datetime': format_datetime
        }
    
    # Register blueprints within app context
    with app.app_context():
        # Import routes here to avoid circular imports
        from app.routes import main_routes, book_routes, user_routes, borrow_routes
        
        # Register each blueprint
        app.register_blueprint(main_routes.bp)
        app.register_blueprint(book_routes.bp)
        app.register_blueprint(user_routes.bp)
        app.register_blueprint(borrow_routes.bp)
        
        # Create database tables
        db.create_all()
        
        # Log successful blueprint registration
        app.logger.info('Successfully registered all blueprints')
    
    return app

# Import models to ensure they are registered with SQLAlchemy
# These imports are placed at the bottom to avoid circular dependencies
from app.models import book, user, borrow