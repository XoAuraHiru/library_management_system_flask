from typing import List
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from app import db

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255))
    publication_year = db.Column(db.Integer)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationship to BorrowRecord
    borrow_records = db.relationship(
        'BorrowRecord',
        back_populates='book',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Book {self.title}>"
    
    @property
    def is_available(self) -> bool:
        return self.available_quantity > 0
