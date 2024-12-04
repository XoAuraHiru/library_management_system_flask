from typing import List
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
import enum

class UserType(enum.Enum):
    """Enumeration for user types."""
    STUDENT = 'student'
    STAFF = 'staff'

class User(Base):
    """User model with modern SQLAlchemy features."""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20))
    
    # Relationship
    borrow_records: Mapped[List["BorrowRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'
    
    @property
    def active_borrows(self) -> List["BorrowRecord"]:
        return [br for br in self.borrow_records if br.status == BorrowStatus.BORROWED]