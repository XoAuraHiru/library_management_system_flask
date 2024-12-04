# app/routes/dashboard.py
from flask import Blueprint, render_template
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.models.book import Book
from app.models.user import User, UserType
from app.models.borrow import BorrowRecord, BorrowStatus
from typing import Dict, List, Any
import logging

bp = Blueprint('dashboard', __name__)

def get_monthly_statistics() -> Dict[str, List[Any]]:
    """Calculate monthly borrowing and return statistics.
    
    Returns:
        Dictionary containing labels and data for the monthly statistics chart.
    """
    try:
        # Get the last 6 months
        today = datetime.utcnow()
        months = []
        borrows = []
        returns = []
        
        for i in range(5, -1, -1):
            # Calculate start and end of month
            end_date = today.replace(day=1) - timedelta(days=1)
            start_date = end_date.replace(day=1)
            
            # Format month label
            months.append(start_date.strftime('%B %Y'))
            
            # Count borrows and returns for the month
            month_borrows = BorrowRecord.query.filter(
                and_(
                    BorrowRecord.borrow_date >= start_date,
                    BorrowRecord.borrow_date <= end_date
                )
            ).count()
            
            month_returns = BorrowRecord.query.filter(
                and_(
                    BorrowRecord.return_date >= start_date,
                    BorrowRecord.return_date <= end_date
                )
            ).count()
            
            borrows.append(month_borrows)
            returns.append(month_returns)
            
            # Move to previous month
            today = start_date
            
        return {
            'labels': months[::-1],
            'borrows': borrows[::-1],
            'returns': returns[::-1]
        }
    except Exception as e:
        logging.error(f"Error calculating monthly statistics: {str(e)}")
        return {'labels': [], 'borrows': [], 'returns': []}

def get_popular_books(limit: int = 5) -> List[Dict[str, Any]]:
    """Get the most frequently borrowed books.
    
    Args:
        limit: Maximum number of books to return
        
    Returns:
        List of dictionaries containing book information and borrow counts
    """
    try:
        return db.session.query(
            Book,
            func.count(BorrowRecord.id).label('borrow_count')
        ).join(BorrowRecord).group_by(Book.id).order_by(
            func.count(BorrowRecord.id).desc()
        ).limit(limit).all()
    except Exception as e:
        logging.error(f"Error retrieving popular books: {str(e)}")
        return []

def get_recent_activities(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent library activities.
    
    Args:
        limit: Maximum number of activities to return
        
    Returns:
        List of dictionaries containing activity information
    """
    try:
        activities = []
        recent_borrows = BorrowRecord.query.order_by(
            BorrowRecord.created_at.desc()
        ).limit(limit).all()
        
        for borrow in recent_borrows:
            if borrow.status == BorrowStatus.BORROWED:
                activity_type = 'borrow'
                description = f"{borrow.user.full_name} borrowed {borrow.book.title}"
            elif borrow.status == BorrowStatus.RETURNED:
                activity_type = 'return'
                description = f"{borrow.user.full_name} returned {borrow.book.title}"
            elif borrow.status == BorrowStatus.OVERDUE:
                activity_type = 'overdue'
                description = f"Overdue: {borrow.book.title} by {borrow.user.full_name}"
            
            activities.append({
                'type': activity_type,
                'description': description,
                'timestamp': borrow.created_at
            })
            
        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)
    except Exception as e:
        logging.error(f"Error retrieving recent activities: {str(e)}")
        return []

def generate_alerts() -> List[Dict[str, Any]]:
    """Generate system alerts based on current library status.
    
    Returns:
        List of dictionaries containing alert information
    """
    try:
        alerts = []
        current_time = datetime.utcnow()
        
        # Check for overdue books
        overdue_count = BorrowRecord.query.filter(
            and_(
                BorrowRecord.status == BorrowStatus.BORROWED,
                BorrowRecord.due_date < current_time
            )
        ).count()
        
        if overdue_count > 0:
            alerts.append({
                'title': 'Overdue Books',
                'description': f'{overdue_count} books are overdue',
                'severity': 'danger',
                'count': overdue_count
            })
        
        # Check for books due today
        due_today_count = BorrowRecord.query.filter(
            and_(
                BorrowRecord.status == BorrowStatus.BORROWED,
                func.date(BorrowRecord.due_date) == func.date(current_time)
            )
        ).count()
        
        if due_today_count > 0:
            alerts.append({
                'title': 'Due Today',
                'description': f'{due_today_count} books are due today',
                'severity': 'warning',
                'count': due_today_count
            })
        
        # Check for low stock books (less than 2 copies available)
        low_stock_count = Book.query.filter(
            Book.available_quantity < 2
        ).count()
        
        if low_stock_count > 0:
            alerts.append({
                'title': 'Low Stock Alert',
                'description': f'{low_stock_count} books are running low on copies',
                'severity': 'info',
                'count': low_stock_count
            })
        
        return alerts
    except Exception as e:
        logging.error(f"Error generating alerts: {str(e)}")
        return []

@bp.route('/')
def dashboard() -> str:
    """Render the main dashboard with all necessary data.
    
    Returns:
        Rendered dashboard template with context data
    """
    try:
        current_time = datetime.utcnow()
        
        # Get various counts for dashboard metrics
        total_books = Book.query.count()
        available_books = Book.query.with_entities(
            func.sum(Book.available_quantity)
        ).scalar() or 0
        borrowed_books = Book.query.with_entities(
            func.sum(Book.quantity - Book.available_quantity)
        ).scalar() or 0
        
        total_users = User.query.count()
        student_count = User.query.filter_by(user_type=UserType.STUDENT).count()
        staff_count = User.query.filter_by(user_type=UserType.STAFF).count()
        
        active_borrows = BorrowRecord.query.filter_by(
            status=BorrowStatus.BORROWED
        ).count()
        
        # Get counts for attention items
        overdue_count = BorrowRecord.query.filter(
            and_(
                BorrowRecord.status == BorrowStatus.BORROWED,
                BorrowRecord.due_date < current_time
            )
        ).count()
        
        due_today = BorrowRecord.query.filter(
            and_(
                BorrowRecord.status == BorrowStatus.BORROWED,
                func.date(BorrowRecord.due_date) == func.date(current_time)
            )
        ).count()
        
        low_stock_count = Book.query.filter(
            Book.available_quantity < 2
        ).count()
        
        attention_count = overdue_count + due_today + low_stock_count
        
        # Gather all required data for the dashboard
        context = {
            'current_time': current_time,
            'total_books': total_books,
            'available_books': available_books,
            'borrowed_books': borrowed_books,
            'total_users': total_users,
            'student_count': student_count,
            'staff_count': staff_count,
            'active_borrows': active_borrows,
            'due_today': due_today,
            'overdue_count': overdue_count,
            'low_stock_count': low_stock_count,
            'attention_count': attention_count,
            'recent_activities': get_recent_activities(),
            'alerts': generate_alerts(),
            'popular_books': get_popular_books(),
            'monthly_stats': get_monthly_statistics()
        }
        
        return render_template('dashboard.html', **context)
        
    except Exception as e:
        logging.error(f"Error rendering dashboard: {str(e)}")
        return render_template('error.html', 
                             message="Error loading dashboard. Please try again later.")