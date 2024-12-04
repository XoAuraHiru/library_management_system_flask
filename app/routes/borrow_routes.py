from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from typing import Union, List, Optional
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app import db
from app.models.book import Book
from app.models.user import User
from app.models.borrow import BorrowRecord, BorrowStatus
from config import Config

bp = Blueprint('borrows', __name__, url_prefix='/borrows')

@bp.route('/')
def list_borrows() -> str:
    """Display all borrowing records.
    
    Returns:
        Rendered template with borrowing records, ordered by date
    """
    try:
        # Get filter parameters
        status = request.args.get('status')
        user_id = request.args.get('user_id')
        
        # Build query with filters
        query = BorrowRecord.query
        
        if status:
            query = query.filter(BorrowRecord.status == BorrowStatus(status))
        if user_id:
            query = query.filter(BorrowRecord.user_id == int(user_id))
        
        # Execute query and order by borrow date
        borrows: List[BorrowRecord] = query.order_by(
            BorrowRecord.borrow_date.desc()
        ).all()
        
        # Update status for any overdue items
        current_time = datetime.utcnow()
        for borrow in borrows:
            if (borrow.status == BorrowStatus.BORROWED and 
                current_time > borrow.due_date):
                borrow.status = BorrowStatus.OVERDUE
        
        db.session.commit()
        
        return render_template('borrows/list.html', 
                             borrows=borrows,
                             BorrowStatus=BorrowStatus)
                             
    except Exception as e:
        current_app.logger.error(f"Error retrieving borrows: {str(e)}")
        flash("Unable to retrieve borrowing records at this time.", "error")
        return render_template('borrows/list.html', 
                             borrows=[],
                             BorrowStatus=BorrowStatus)

@bp.route('/add', methods=['GET', 'POST'])
def add_borrow() -> Union[str, Response]:
    """Create a new borrowing record.
    
    Handles both form display and processing of new book loans.
    Includes validation of book availability and user borrowing limits.
    
    Returns:
        Either rendered template (GET) or redirect response (POST)
    """
    if request.method == 'POST':
        try:
            book_id = int(request.form['book_id'])
            user_id = int(request.form['user_id'])
            
            # Get book and user records
            book: Optional[Book] = Book.query.get_or_404(book_id)
            user: Optional[User] = User.query.get_or_404(user_id)
            
            # Validate book availability
            if book.available_quantity <= 0:
                flash('This book is not available for borrowing.', 'error')
                return redirect(url_for('borrows.add_borrow'))
            
            # Check user's active borrows (implement borrowing limits)
            max_borrows = 3 if user.user_type == UserType.STUDENT else 5
            if len(user.active_borrows) >= max_borrows:
                flash(f'User has reached the maximum limit of {max_borrows} active borrows.', 'error')
                return redirect(url_for('borrows.add_borrow'))
            
            # Calculate due date based on configuration
            borrow_duration = current_app.config.get('BORROW_DURATION', timedelta(days=14))
            due_date = datetime.utcnow() + borrow_duration
            
            # Create borrow record
            borrow = BorrowRecord(
                book_id=book_id,
                user_id=user_id,
                borrow_date=datetime.utcnow(),
                due_date=due_date,
                status=BorrowStatus.BORROWED
            )
            
            # Update book availability and save records
            book.available_quantity -= 1
            db.session.add(borrow)
            db.session.commit()
            
            flash('Book borrowed successfully!', 'success')
            return redirect(url_for('borrows.list_borrows'))
            
        except ValueError:
            flash('Invalid book or user selection.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing borrow: {str(e)}")
            flash('Error processing borrow request. Please try again.', 'error')
    
    # For GET request or if POST failed, show the form with available books and users
    try:
        available_books = Book.query.filter(Book.available_quantity > 0).order_by(Book.title).all()
        users = User.query.order_by(User.last_name, User.first_name).all()
        return render_template('borrows/add.html', 
                             books=available_books,
                             users=users)
    except Exception as e:
        current_app.logger.error(f"Error loading borrow form: {str(e)}")
        flash("Unable to load the borrow form. Please try again.", "error")
        return redirect(url_for('borrows.list_borrows'))

@bp.route('/return/<int:id>', methods=['POST'])
def return_book(id: int) -> Response:
    """Process a book return.
    
    Updates the borrow record status and adjusts book availability.
    Calculates any late fees if applicable.
    
    Args:
        id: The ID of the borrow record to process
        
    Returns:
        Redirect response
    """
    borrow = BorrowRecord.query.get_or_404(id)
    
    if borrow.status == BorrowStatus.RETURNED:
        flash('This book has already been returned.', 'error')
        return redirect(url_for('borrows.list_borrows'))
    
    try:
        # Process the return
        return_date = datetime.utcnow()
        borrow.return_date = return_date
        borrow.status = BorrowStatus.RETURNED
        
        # Update book availability
        borrow.book.available_quantity += 1
        
        # Calculate and record late fee if applicable
        if return_date > borrow.due_date:
            days_late = (return_date - borrow.due_date).days
            fee_per_day = current_app.config.get('LATE_FEE_PER_DAY', 1.00)
            late_fee = days_late * fee_per_day
            flash(f'Late return fee: ${late_fee:.2f}', 'warning')
        
        db.session.commit()
        flash('Book returned successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing return: {str(e)}")
        flash('Error processing return. Please try again.', 'error')
    
    return redirect(url_for('borrows.list_borrows'))

@bp.route('/extend/<int:id>', methods=['POST'])
def extend_borrow(id: int) -> Response:
    """Extend the borrowing period for a book.
    
    Allows one extension per borrow, adding a specified number of days
    to the due date if the book is not already overdue.
    
    Args:
        id: The ID of the borrow record to extend
        
    Returns:
        Redirect response
    """
    borrow = BorrowRecord.query.get_or_404(id)
    
    try:
        # Check if extension is allowed
        if borrow.status != BorrowStatus.BORROWED:
            flash('Can only extend active borrows.', 'error')
            return redirect(url_for('borrows.list_borrows'))
        
        if borrow.is_overdue():
            flash('Cannot extend overdue borrows.', 'error')
            return redirect(url_for('borrows.list_borrows'))
        
        # Calculate new due date
        extension_days = current_app.config.get('EXTENSION_DAYS', 7)
        borrow.due_date = borrow.due_date + timedelta(days=extension_days)
        
        db.session.commit()
        flash(f'Borrowing period extended by {extension_days} days.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error extending borrow: {str(e)}")
        flash('Error extending borrowing period. Please try again.', 'error')
    
    return redirect(url_for('borrows.list_borrows'))