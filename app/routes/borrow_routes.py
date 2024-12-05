from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from typing import Union, List, Optional
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app import db
from app.models.book import Book
from app.models.user import User, UserType  # Added UserType import
from app.models.borrow import BorrowRecord, BorrowStatus
from config import Config

bp = Blueprint('borrows', __name__, url_prefix='/borrows')

@bp.route('/')
def list_borrows() -> str:
    try:
        status = request.args.get('status')
        user_id = request.args.get('user_id')
        
        query = BorrowRecord.query
        
        if status:
            query = query.filter(BorrowRecord.status == BorrowStatus(status))
        if user_id:
            query = query.filter(BorrowRecord.user_id == int(user_id))
        
        borrows: List[BorrowRecord] = query.order_by(
            BorrowRecord.borrow_date.desc()
        ).all()
        
        current_time = datetime.utcnow()
        for borrow in borrows:
            if (borrow.status == BorrowStatus.BORROWED and 
                current_time > borrow.due_date):
                borrow.status = BorrowStatus.OVERDUE
        
        db.session.commit()
        
        today = datetime.utcnow().date()
        
        return render_template('borrows/list.html', 
                             borrows=borrows,
                             BorrowStatus=BorrowStatus,
                             today=today)
                             
    except Exception as e:
        current_app.logger.error(f"Error retrieving borrows: {str(e)}")
        flash("Unable to retrieve borrowing records at this time.", "error")
        return render_template('borrows/list.html', 
                             borrows=[],
                             BorrowStatus=BorrowStatus,
                             today=datetime.utcnow().date())

@bp.route('/add', methods=['GET', 'POST'])
def add_borrow() -> Union[str, Response]:
    if request.method == 'POST':
        try:
            book_id = int(request.form['book_id'])
            user_id = int(request.form['user_id'])
            
            book: Optional[Book] = Book.query.get_or_404(book_id)
            user: Optional[User] = User.query.get_or_404(user_id)
            
            if book.available_quantity <= 0:
                flash('This book is not available for borrowing.', 'error')
                return redirect(url_for('borrows.add_borrow'))
            
            max_borrows = 3 if user.user_type == UserType.STUDENT else 5
            if len(user.active_borrows) >= max_borrows:
                flash(f'User has reached the maximum limit of {max_borrows} active borrows.', 'error')
                return redirect(url_for('borrows.add_borrow'))
            
            borrow_duration = current_app.config.get('BORROW_DURATION', timedelta(days=14))
            due_date = datetime.utcnow() + borrow_duration
            
            borrow = BorrowRecord(
                book_id=book_id,
                user_id=user_id,
                borrow_date=datetime.utcnow(),
                due_date=due_date,
                status=BorrowStatus.BORROWED
            )
            
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
    borrow = BorrowRecord.query.get_or_404(id)
    
    if borrow.status == BorrowStatus.RETURNED:
        flash('This book has already been returned.', 'error')
        return redirect(url_for('borrows.list_borrows'))
    
    try:
        return_date = datetime.utcnow()
        borrow.return_date = return_date
        borrow.status = BorrowStatus.RETURNED
        
        borrow.book.available_quantity += 1
        
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
    borrow = BorrowRecord.query.get_or_404(id)
    
    try:
        if borrow.status != BorrowStatus.BORROWED:
            flash('Can only extend active borrows.', 'error')
            return redirect(url_for('borrows.list_borrows'))
        
        if borrow.is_overdue():
            flash('Cannot extend overdue borrows.', 'error')
            return redirect(url_for('borrows.list_borrows'))
        
        extension_days = current_app.config.get('EXTENSION_DAYS', 7)
        borrow.due_date = borrow.due_date + timedelta(days=extension_days)
        
        db.session.commit()
        flash(f'Borrowing period extended by {extension_days} days.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error extending borrow: {str(e)}")
        flash('Error extending borrowing period. Please try again.', 'error')
    
    return redirect(url_for('borrows.list_borrows'))