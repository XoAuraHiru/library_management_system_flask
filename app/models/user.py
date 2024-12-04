from datetime import datetime
from enum import Enum
from sqlalchemy.ext.hybrid import hybrid_property
from ..db import db

class UserType(Enum):
    """Defines the types of users in the library system.
    Used to determine borrowing privileges and access levels."""
    STUDENT = 'STUDENT'
    FACULTY = 'FACULTY'
    STAFF = 'STAFF'

class User(db.Model):
    """Represents a library user who can borrow books.
    
    This model includes personal information, contact details,
    and relationships to track borrowing history."""
    
    __tablename__ = 'users'
    
    # Primary key and basic user information
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))  # Optional phone number
    
    # New timestamp fields
    created_at = db.Column(db.DateTime, nullable=False, 
                          default=datetime.utcnow,
                          server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow,
                          server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # Borrowing limits based on user type
    max_borrow_limit = db.Column(db.Integer, nullable=False, default=3)  # Default for students
    
    # Relationships
    borrow_records = db.relationship(
        'BorrowRecord',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        """Initialize a new user, setting appropriate borrowing limits based on user type."""
        super(User, self).__init__(**kwargs)
        # Set higher borrowing limit for staff/faculty
        if self.user_type in (UserType.STAFF, UserType.FACULTY):
            self.max_borrow_limit = 5

    @hybrid_property
    def active_borrows(self):
        """Returns a list of currently borrowed books that haven't been returned."""
        from .borrow import BorrowStatus  # Import here to avoid circular imports
        return [record for record in self.borrow_records 
                if record.status == BorrowStatus.BORROWED]

    @property
    def active_borrows_count(self):
        """Returns the count of currently borrowed books."""
        return len(self.active_borrows)

    @property
    def can_borrow(self):
        """Checks if the user can borrow more books based on their limit."""
        return self.active_borrows_count < self.max_borrow_limit

    @property
    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """String representation of the user."""
        return f"<User {self.id}: {self.full_name} ({self.user_type.value})>"