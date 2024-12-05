# book_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.book import Book

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/')
def list_books():
    try:
        books = Book.query.order_by(Book.title).all()
        return render_template('books/list.html', books=books)
    except Exception as e:
        current_app.logger.error(f"Error retrieving books: {str(e)}")
        return render_template('books/list.html', books=[])

@bp.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            book = Book(
                isbn=request.form['isbn'].strip(),
                title=request.form['title'].strip(),
                author=request.form['author'].strip(),
                publisher=request.form.get('publisher', '').strip(),
                publication_year=int(request.form['publication_year']),
                quantity=int(request.form['quantity'])
            )
            book.available_quantity = book.quantity
            
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books.list_books'))
            
        except IntegrityError:
            db.session.rollback()
            flash('A book with this ISBN already exists.', 'error')
        except ValueError:
            flash('Please enter valid numeric values for year and quantity.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding book: {str(e)}")
            flash('Error adding book. Please try again.', 'error')
    
    return render_template('books/add.html', current_year=datetime.now().year)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get the minimum allowed quantity (currently borrowed copies)
            min_quantity = book.quantity - book.available_quantity
            new_quantity = int(request.form['quantity'])
            
            if new_quantity < min_quantity:
                flash(f'Quantity cannot be less than {min_quantity} (currently borrowed copies).', 'error')
                return render_template('books/edit.html', book=book, current_year=datetime.now().year)
            
            # Update book attributes
            book.title = request.form['title'].strip()
            book.author = request.form['author'].strip()
            book.publisher = request.form.get('publisher', '').strip()
            book.publication_year = int(request.form['publication_year'])
            
            # Update quantity and available_quantity
            quantity_difference = new_quantity - book.quantity
            book.quantity = new_quantity
            book.available_quantity += quantity_difference
            
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('books.list_books'))
            
        except ValueError:
            flash('Please enter valid numeric values for year and quantity.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating book: {str(e)}")
            flash('Error updating book. Please try again.', 'error')
    
    return render_template('books/edit.html', book=book, current_year=datetime.now().year)

@bp.route('/delete/<int:id>')
def delete_book(id):
    book = Book.query.get_or_404(id)
    
    if book.quantity != book.available_quantity:
        flash('Cannot delete book while copies are borrowed.', 'error')
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