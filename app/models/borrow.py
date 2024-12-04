from datetime import datetime
from enum import Enum
from ..db import db

class BorrowStatus(Enum):
    BORROWED = 'BORROWED'
    RETURNED = 'RETURNED'
    OVERDUE = 'OVERDUE'

class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED)

    # Relationships
    book = db.relationship('Book', back_populates='borrow_records')
    user = db.relationship('User', back_populates='borrow_records')

    def __repr__(self):
        return f"<BorrowRecord {self.id}>"

    def is_overdue(self):
        if self.status == BorrowStatus.BORROWED:
            return datetime.utcnow() > self.due_date
        return False

    def return_book(self):
        if self.status != BorrowStatus.RETURNED:
            self.status = BorrowStatus.RETURNED
            self.return_date = datetime.utcnow()
            self.book.available_quantity += 1
            db.session.commit()