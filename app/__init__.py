# app/__init__.py
from pathlib import Path
from flask import Flask
from typing import Optional, Type
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
from config import Config
from .db import db, migrate

# Load environment variables
load_dotenv()

def create_app(config_class: Optional[Type[Config]] = None) -> Flask:
    app = Flask(__name__)
    
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
    
    # Register blueprints
    with app.app_context():
        from app.routes import book_routes, user_routes, borrow_routes
        app.register_blueprint(book_routes.bp)
        app.register_blueprint(user_routes.bp)
        app.register_blueprint(borrow_routes.bp)
        
        # Create database tables
        db.create_all()
    
    return app