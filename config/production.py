import os
from datetime import timedelta

class ProductionConfig:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key'
    DEBUG = False

    # Database configuration 
    MYSQL_HOST: str = os.getenv('MYSQL_HOST')
    MYSQL_USER: str = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB: str = os.getenv('MYSQL_DB')
    
    # Database configuration - PythonAnywhere format
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://yourusername:your-mysql-password@yourusername.mysql.pythonanywhere-services.com/yourusername$library_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    
    # Borrowing settings
    BORROW_DURATION = timedelta(days=14)
    EXTENSION_DAYS = 7
    LATE_FEE_PER_DAY = 1.00