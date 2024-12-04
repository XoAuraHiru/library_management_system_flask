from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
import enum

class BorrowStatus(enum.Enum):
    """Enumeration for borrow status."""
    BORROWED = 'borrowed'
    RETURNED = 'returned'
    OVERDUE = 'overdue'

class BorrowRecord(Base):
    """Borrow record model with modern SQLAlchemy features."""
    __tablename__ = 'borrow_records'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    borrow_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    return_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[BorrowStatus] = mapped_column(
        Enum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED
    )
    
    # Relationships
    book: Mapped["Book"] = relationship(back_populates="borrow_records")
    user: Mapped["User"] = relationship(back_populates="borrow_records")
    
    def __repr__(self) -> str:
        return f'<BorrowRecord {self.id}>'
    
    def is_overdue(self) -> bool:
        """Check if the borrowed book is overdue."""
        if self.status == BorrowStatus.BORROWED:
            return datetime.utcnow() > self.due_date
        return False
    
    def return_book(self) -> None:
        """Process a book return."""
        if self.status != BorrowStatus.RETURNED:
            self.status = BorrowStatus.RETURNED
            self.return_date = datetime.utcnow()
            self.book.available_quantity += 1