from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from typing import Union, List
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.book import Book
from datetime import datetime

# Create a blueprint with a URL prefix
bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/', methods=['GET'])
def list_books() -> str:
    """Display all books in the library.
    
    Retrieves all books from the database and passes them to the template
    for rendering. Books are ordered by title for easy browsing.
    
    Returns:
        Rendered template with list of books
    """
    try:
        books: List[Book] = Book.query.order_by(Book.title).all()
        return render_template('books/list.html', books=books)
    except Exception as e:
        # Log the error and show a user-friendly message
        current_app.logger.error(f"Error retrieving books: {str(e)}")
        flash("Unable to retrieve books at this time.", "error")
        return render_template('books/list.html', books=[])

@bp.route('/add', methods=['GET', 'POST'])
def add_book() -> Union[str, Response]:
    """Add a new book to the library.
    
    GET: Display the book addition form
    POST: Process the form submission and create a new book
    
    Returns:
        Either rendered template (GET) or redirect response (POST)
    """
    if request.method == 'POST':
        try:
            # Create a new book instance with form data
            book = Book(
                isbn=request.form['isbn'].strip(),
                title=request.form['title'].strip(),
                author=request.form['author'].strip(),
                publisher=request.form.get('publisher', '').strip(),
                publication_year=int(request.form['publication_year']),
                quantity=int(request.form['quantity']),
                available_quantity=int(request.form['quantity'])
            )
            
            # Validate the book data before saving
            if not book.isbn or not book.title or not book.author:
                flash("Please fill in all required fields.", "error")
                return render_template('books/add.html')
            
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books.list_books'))
            
        except IntegrityError:
            db.session.rollback()
            flash('A book with this ISBN already exists.', 'error')
        except ValueError:
            flash('Please enter valid numbers for quantity and year.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding book: {str(e)}")
            flash('Error adding book. Please try again.', 'error')
    
    return render_template('books/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id: int) -> Union[str, Response]:
    """Edit an existing book's details.
    
    Args:
        id: The ID of the book to edit
    
    Returns:
        Either rendered template (GET) or redirect response (POST)
    """
    book = Book.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update book attributes from form data
            book.isbn = request.form['isbn'].strip()
            book.title = request.form['title'].strip()
            book.author = request.form['author'].strip()
            book.publisher = request.form.get('publisher', '').strip()
            book.publication_year = int(request.form['publication_year'])
            
            # Validate updated data
            if not book.isbn or not book.title or not book.author:
                flash("Please fill in all required fields.", "error")
                return render_template('books/edit.html', book=book)
            
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('books.list_books'))
            
        except IntegrityError:
            db.session.rollback()
            flash('A book with this ISBN already exists.', 'error')
        except ValueError:
            flash('Please enter a valid publication year.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating book: {str(e)}")
            flash('Error updating book. Please try again.', 'error')
    
    return render_template('books/edit.html', book=book)

@bp.route('/delete/<int:id>')
def delete_book(id: int) -> Response:
    """Delete a book from the library.
    
    Args:
        id: The ID of the book to delete
    
    Returns:
        Redirect response
    """
    book = Book.query.get_or_404(id)
    
    # Check if book can be deleted (no active borrows)
    if book.available_quantity < book.quantity:
        flash('Cannot delete book while it is borrowed by users.', 'error')
        return redirect(url_for('books.list_books'))
    
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting book: {str(e)}")
        flash('Error deleting book. Please try again.', 'error')
    
    return redirect(url_for('books.list_books'))