from dataclasses import dataclass
from datetime import timedelta
from typing import Optional
import os
from pathlib import Path

from dotenv import load_dotenv # type: ignore
load_dotenv()

@dataclass
class Config:
    """Application configuration using Python 3.12 features and type hints."""
    # Database configuration with fallback values
    MYSQL_HOST: str = os.getenv('MYSQL_HOST')
    MYSQL_USER: str = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB: str = os.getenv('MYSQL_DB')
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI: str = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # Application configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', os.urandom(32).hex())
    BORROW_DURATION: timedelta = timedelta(days=14)
    
    # Security configuration
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    
    # Upload configuration
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024
    UPLOAD_FOLDER: Path = Path(os.getenv('UPLOAD_FOLDER', 'uploads'))