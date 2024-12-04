# Library Management System

Welcome to our Library Management System, a modern web application built with Flask and MySQL that helps librarians efficiently manage their book collections, user records, and borrowing operations. This system is designed to be user-friendly while maintaining robust data integrity and security.

## Features

The system provides comprehensive library management capabilities through these core modules:

### Book Management
Our book management module allows librarians to maintain a detailed catalog of the library's collection. You can:
- Add new books with detailed information including ISBN, title, author, and quantity
- Track multiple copies of the same book independently
- Monitor book availability in real-time
- Update book information as needed
- Remove books from the catalog when necessary

### User Management
The user management system supports different types of library members with varying privileges:
- Register new students and staff members
- Maintain member contact information
- Track borrowing history for each user
- Enforce different borrowing limits (3 books for students, 5 for staff)
- Monitor active loans per user

### Borrowing System
Our borrowing module streamlines the loan process with features like:
- Quick book checkout with automatic due date calculation
- Configurable loan periods (1 week to 1 month)
- Real-time availability checking
- Overdue tracking and notifications
- Simple book return processing
- Complete borrowing history

### Dashboard
The dashboard provides an at-a-glance view of the library's status:
- Current borrowing statistics
- Overdue book alerts
- Popular books tracking
- User activity monitoring
- Monthly borrowing trends

## Technical Requirements

Before installing the system, ensure your environment meets these requirements:

- Python 3.12 or higher
- MySQL 8.0 or higher
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- 1GB of free disk space (minimum)
- 2GB RAM (recommended)

## Installation Guide

Follow these steps to set up the Library Management System:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/library-management.git
   cd library-management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the MySQL database:
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE library_db;
   ```

5. Configure environment variables by creating a `.env` file:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_DB=library_db
   SECRET_KEY=your-secure-secret-key
   ```

6. Initialize the database:
   ```bash
   python -m flask db upgrade
   ```

7. Start the application:
   ```bash
   python run.py
   ```

The system will be available at `http://localhost:5000`

## User Guide

### Getting Started
When you first access the system, you'll see the dashboard showing key library statistics. The navigation menu provides access to all main functions:

### Managing Books
To add a new book:
1. Click "Books" in the navigation menu
2. Click "Add New Book"
3. Fill in the book details (ISBN, title, author, etc.)
4. Specify the number of copies
5. Click "Save Book"

To manage existing books:
1. Go to the Books list
2. Use the search box to find specific books
3. Click "Edit" to modify book details or "Delete" to remove a book
4. The availability indicator shows current status

### Managing Users
To register a new user:
1. Click "Users" in the navigation menu
2. Click "Add New User"
3. Select the user type (student/staff)
4. Fill in personal and contact information
5. Click "Add User"

User management tips:
- Staff members can borrow up to 5 books
- Students can borrow up to 3 books
- Users with active borrows cannot be deleted
- Email addresses must be unique

### Processing Loans
To create a new borrowing record:
1. Click "Borrowing" in the navigation menu
2. Click "New Borrow"
3. Select the user from the dropdown
4. Choose the book to be borrowed
5. Set the borrowing period
6. Confirm the details and submit

When processing returns:
1. Find the borrowing record
2. Click the "Return" button
3. Confirm the return
4. The system will automatically update availability

## Troubleshooting

Common issues and solutions:

### Database Connection Errors
- Verify MySQL is running
- Check database credentials in .env file
- Ensure database name matches configuration

### Book Not Available for Borrowing
- Check current availability count
- Verify no pending transactions
- Ensure book status is active

### User Cannot Borrow
- Check current borrowing count against limit
- Verify user account is active
- Check for overdue books

## Maintenance

To keep the system running smoothly:

1. Regular Backups
   ```bash
   mysqldump -u root -p library_db > backup.sql
   ```

2. Log Monitoring
   - Check logs/library.log for errors
   - Monitor disk space usage
   - Review access patterns

3. Database Optimization
   ```sql
   ANALYZE TABLE books, users, borrow_records;
   ```

## Security Considerations

The system implements several security measures:
- Password hashing for user credentials
- CSRF protection for forms
- Input validation and sanitization
- Secure session handling
- SQL injection prevention

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please follow our coding standards and include appropriate tests.

## Support

For support:
- Check the troubleshooting guide above
- Review our documentation
- Submit issues through the issue tracker
- Contact library-support@yourdomain.com

## License

This Library Management System is released under the MIT License. See LICENSE file for details.

---

For more detailed information about specific features or technical aspects, please consult our [Wiki](link-to-wiki) or contact the development team.