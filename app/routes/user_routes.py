from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from typing import Union, List
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.user import User, UserType
from email_validator import validate_email, EmailNotValidError

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def list_users() -> str:
    """Display all library users.
    
    Returns:
        Rendered template with list of users, ordered by name
    """
    try:
        users: List[User] = User.query.order_by(User.last_name, User.first_name).all()
        return render_template('users/list.html', users=users)
    except Exception as e:
        current_app.logger.error(f"Error retrieving users: {str(e)}")
        flash("Unable to retrieve users at this time.", "error")
        return render_template('users/list.html', users=[])

@bp.route('/add', methods=['GET', 'POST'])
def add_user() -> Union[str, Response]:
    """Add a new library user.
    
    Handles both the display of the user addition form and processing
    of form submissions. Includes validation for email format and
    required fields.
    
    Returns:
        Either rendered template (GET) or redirect response (POST)
    """
    if request.method == 'POST':
        try:
            # Validate email format
            email = request.form['email'].strip()
            validate_email(email)
            
            # Create new user instance
            user = User(
                user_type=UserType(request.form['user_type']),
                first_name=request.form['first_name'].strip(),
                last_name=request.form['last_name'].strip(),
                email=email,
                phone=request.form.get('phone', '').strip()
            )
            
            # Validate required fields
            if not user.first_name or not user.last_name:
                flash("Please fill in all required fields.", "error")
                return render_template('users/add.html')
            
            db.session.add(user)
            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('users.list_users'))
            
        except EmailNotValidError:
            flash('Please enter a valid email address.', 'error')
        except IntegrityError:
            db.session.rollback()
            flash('A user with this email already exists.', 'error')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding user: {str(e)}")
            flash('Error adding user. Please try again.', 'error')
    
    # For GET request or if POST failed, show the form
    return render_template('users/add.html', user_types=UserType)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id: int) -> Union[str, Response]:
    """Edit an existing user's details.
    
    Args:
        id: The ID of the user to edit
        
    Returns:
        Either rendered template (GET) or redirect response (POST)
    """
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Validate email format
            email = request.form['email'].strip()
            validate_email(email)
            
            # Update user attributes
            user.user_type = UserType(request.form['user_type'])
            user.first_name = request.form['first_name'].strip()
            user.last_name = request.form['last_name'].strip()
            user.email = email
            user.phone = request.form.get('phone', '').strip()
            
            # Validate required fields
            if not user.first_name or not user.last_name:
                flash("Please fill in all required fields.", "error")
                return render_template('users/edit.html', user=user, user_types=UserType)
            
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('users.list_users'))
            
        except EmailNotValidError:
            flash('Please enter a valid email address.', 'error')
        except IntegrityError:
            db.session.rollback()
            flash('A user with this email already exists.', 'error')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user: {str(e)}")
            flash('Error updating user. Please try again.', 'error')
    
    return render_template('users/edit.html', user=user, user_types=UserType)

@bp.route('/delete/<int:id>')
def delete_user(id: int) -> Response:
    """Delete a user from the library system.
    
    Checks if the user has any active borrows before deletion.
    
    Args:
        id: The ID of the user to delete
        
    Returns:
        Redirect response
    """
    user = User.query.get_or_404(id)
    
    # Check for active borrows
    if user.active_borrows:
        flash('Cannot delete user while they have active borrows.', 'error')
        return redirect(url_for('users.list_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        flash('Error deleting user. Please try again.', 'error')
    
    return redirect(url_for('users.list_users'))