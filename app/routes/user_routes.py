from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from typing import Union
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from app import db
from app.models.user import User, UserType

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def list_users():
    """Display a list of all library users with their basic information."""
    try:
        users = User.query.order_by(User.last_name, User.first_name).all()
        current_app.logger.debug(f"Found {len(users)} users")
        return render_template('users/list.html', users=users, UserType=UserType)
    except Exception as e:
        current_app.logger.error(f"Error retrieving users: {str(e)}")
        flash('Error loading users. Please try again.', 'error')
        return render_template('users/list.html', users=[], UserType=UserType)

@bp.route('/add', methods=['GET', 'POST'])
def add_user():
    """Handle user creation with proper validation and error handling."""
    if request.method == 'POST':
        try:
            # Validate email format
            email = request.form['email'].strip()
            validate_email(email)
            
            # Create new user with validated data
            user = User(
                first_name=request.form['first_name'].strip(),
                last_name=request.form['last_name'].strip(),
                email=email,
                phone=request.form.get('phone', '').strip(),
                user_type=UserType(request.form['user_type'])
            )
            
            db.session.add(user)
            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('users.list_users'))
            
        except EmailNotValidError:
            flash('Please enter a valid email address.', 'error')
        except IntegrityError:
            db.session.rollback()
            flash('A user with this email already exists.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding user: {str(e)}")
            flash('Error adding user. Please try again.', 'error')
    
    return render_template('users/add.html', UserType=UserType)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id: int) -> Union[str, redirect]:
    """Edit an existing user's details with validation and type checking."""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Validate email format
            email = request.form['email'].strip()
            validate_email(email)
            
            # Check user type change restrictions
            new_type = UserType(request.form['user_type'])
            if (user.user_type == UserType.STAFF and 
                new_type == UserType.STUDENT and 
                user.active_borrows_count > 3):
                flash('Cannot change to student type while having more than 3 active borrows.', 'error')
                return render_template('users/edit.html', user=user, UserType=UserType)
            
            # Update user attributes
            user.user_type = new_type
            user.first_name = request.form['first_name'].strip()
            user.last_name = request.form['last_name'].strip()
            user.email = email
            user.phone = request.form.get('phone', '').strip()
            
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
    
    return render_template('users/edit.html', user=user, UserType=UserType)

@bp.route('/delete/<int:id>')
def delete_user(id: int):
    """Delete a user if they have no active borrows."""
    user = User.query.get_or_404(id)
    
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