# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from typing import Optional, Type
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize SQLAlchemy with type hints
db = SQLAlchemy()

def create_app(config_class: Optional[Type[Config]] = None) -> Flask:
    """
    Factory function to create and configure the Flask application.
    
    Args:
        config_class: Optional configuration class to use instead of default Config
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = Config
    app.config.from_object(config_class)
    
    # Ensure upload folder exists
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    upload_folder.mkdir(exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure logging
    if not app.debug and not app.testing:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
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
    
    # Register blueprints
    with app.app_context():
        from app.routes import book_routes, user_routes, borrow_routes
        app.register_blueprint(book_routes.bp)
        app.register_blueprint(user_routes.bp)
        app.register_blueprint(borrow_routes.bp)
        
        # Create database tables
        db.create_all()
    
    return app

# run.py
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)