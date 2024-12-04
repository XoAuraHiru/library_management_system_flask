# app/db.py
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_migrate import Migrate # type: ignore

db = SQLAlchemy()
migrate = Migrate()