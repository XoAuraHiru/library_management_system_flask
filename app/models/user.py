# app/models/user.py
from enum import Enum
from ..db import db

class UserType(Enum):
    STUDENT = 'STUDENT'  # Match database values (uppercase)
    FACULTY = 'FACULTY'
    STAFF = 'STAFF'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    max_borrow_limit = db.Column(db.Integer, nullable=False, default=3)

    # Relationships
    borrow_records = db.relationship(
        'BorrowRecord',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"