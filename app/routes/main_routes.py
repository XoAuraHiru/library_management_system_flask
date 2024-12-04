from flask import Blueprint, render_template
from app.models.book import Book
from app.models.user import User
from app.models.borrow import BorrowRecord, BorrowStatus

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage route that displays system overview statistics."""
    # Get basic statistics for the dashboard
    total_books = Book.query.count()
    total_users = User.query.count()
    active_borrows = BorrowRecord.query.filter_by(status=BorrowStatus.BORROWED).count()
    overdue_borrows = BorrowRecord.query.filter(
        BorrowRecord.status == BorrowStatus.BORROWED,
        BorrowRecord.due_date < BorrowRecord.borrow_date
    ).count()

    return render_template('main/index.html',
                         total_books=total_books,
                         total_users=total_users,
                         active_borrows=active_borrows,
                         overdue_borrows=overdue_borrows)