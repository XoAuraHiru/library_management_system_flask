from datetime import datetime
from ..db import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255))
    publication_year = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Add timestamp fields
    created_at = db.Column(db.DateTime, nullable=False, 
                          default=datetime.utcnow,
                          server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow,
                          server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Relationships
    borrow_records = db.relationship(
        'BorrowRecord',
        back_populates='book',
        cascade='all, delete-orphan'
    )

    @property
    def is_available(self):
        return self.available_quantity > 0

    def __repr__(self):
        return f"<Book {self.id}: {self.title}>"