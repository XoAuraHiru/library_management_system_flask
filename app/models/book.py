from typing import List
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Book(Base):
    """Book model with SQLAlchemy 2.0 features."""
    __tablename__ = 'books'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[str] = mapped_column(String(255))
    publication_year: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Relationship
    borrow_records: Mapped[List["BorrowRecord"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f'<Book {self.title}>'
    
    @property
    def is_available(self) -> bool:
        return self.available_quantity > 0
