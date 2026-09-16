# Crescent College Library Management System

A professional web-based Library Book Management System developed for the
**B.S. Abdur Rahman Crescent Institute of Science and Technology
(Crescent College Central Library).**

The system provides a simple interface for managing books, book copies,
categories, authors, shelf information and book-cover images.

---

## Features

### 📚 Book Management

- Add new books
- View all books
- Search books
- View complete book details
- Edit existing books
- Delete books
- Track total copies
- Track available copies
- Track borrowed copies
- Manage shelf numbers
- Store ISBN information
- Store publisher and publication year
- Upload book-cover images

### 📊 Dashboard

The dashboard provides:

- Total number of books
- Total number of copies
- Available copies
- Borrowed copies
- Recently added books
- Quick navigation to major library functions

### 🔎 Search

Books can be searched using:

- Book title
- Author
- ISBN
- Category
- Publisher
- Book ID
- Shelf number

### 🖼️ Book Covers

The system supports:

- PNG
- JPG
- JPEG
- WEBP

Maximum image size:

```text
5 MB
```

### 🔐 Login

The application includes a basic administrator login system.

Demo credentials:

```text
Username: admin
Password: admin123
```

> Change these credentials before using the application in a real deployment.

---

# Project Structure

```text
library_management_system/
│
├── app.py
├── wsgi.py
├── requirements.txt
├── README.md
│
├── data/
│   └── library_books.xlsx
│
├── uploads/
│   └── book_covers/
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── add_book.html
│   ├── books.html
│   ├── edit_book.html
│   └── book_details.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── images/
│       └── logo.png
│
└── utils/
    ├── __init__.py
    ├── excel_manager.py
    ├── image_manager.py
    └── book_manager.py
```

---

# Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2

## Backend

- Python
- Flask

## Database / Storage

The current version uses:

```text
Microsoft Excel (.xlsx)
```

The Excel file is:

```text
data/library_books.xlsx
```

## Image Processing

```text
Pillow
```

## Production Server

```text
Gunicorn
```

---

# Excel Data Structure

The library Excel file uses the following columns:

```text
Book ID
Book Title
Author
ISBN
Category
Publisher
Publication Year
Total Copies
Available Copies
Shelf Number
Cover Image
Date Added
```

---

# Installation

## 1. Clone or open the project

Open the project in GitHub Codespaces, VS Code or another development environment.

---

## 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux / macOS / Codespaces:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

Run:

```bash
pip install -r requirements.txt
```

---

# Run the Application

Start the Flask application using:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

For GitHub Codespaces, open the forwarded port `5000`.

---

# Run Using Gunicorn

For production-style execution:

```bash
gunicorn wsgi:app
```

The `wsgi.py` file contains:

```python
from app import app
```

Therefore Gunicorn can locate the Flask application using:

```text
wsgi:app
```

---

# Render Deployment

## Build Command

Use:

```bash
pip install -r requirements.txt
```

## Start Command

Use:

```bash
gunicorn wsgi:app
```

Do not use:

```text
python app.py
```

as the Render production start command.

---

# Environment Variables

For deployment, configure:

```text
SECRET_KEY
```

Example:

```text
SECRET_KEY=your-secure-random-secret-key
```

Do not publish your real secret key in GitHub.

---

# Default Login

The current development version uses:

```text
Username: admin
Password: admin123
```

These are intended for demonstration/local development.

For production use, replace the demo authentication with a proper user database and secure password hashing.

---

# Book Workflow

The normal workflow is:

```text
Login
  ↓
Dashboard
  ↓
Add Book
  ↓
Enter Book Information
  ↓
Upload Cover Image
  ↓
Generate Book ID
  ↓
Save Book to Excel
  ↓
Book Appears in Catalogue
  ↓
View / Edit / Delete
```

---

# Book Copy Calculation

When a new book is added:

```text
Available Copies = Total Copies
Borrowed Copies = 0
```

For existing books:

```text
Borrowed Copies =
Total Copies - Available Copies
```

The system prevents available copies from exceeding total copies.

---

# API Endpoints

The application also provides basic JSON endpoints.

## Statistics

```text
GET /api/statistics
```

Returns library statistics.

---

## All Books

```text
GET /api/books
```

Returns the books available in the catalogue.

---

## Individual Book

```text
GET /api/books/<book_id>
```

Returns information for a specific book.

---

## Health Check

```text
GET /health
```

Used to check whether the application is running.

---

# Important Directories

## Excel Database

```text
data/library_books.xlsx
```

Do not delete this file if you want to preserve the current catalogue.

---

## Uploaded Covers

```text
uploads/book_covers/
```

Uploaded book-cover images are stored here.

---

## Static Files

```text
static/
```

Contains:

- CSS
- JavaScript
- Logo and other static images

---

# Troubleshooting

## ModuleNotFoundError

If you see:

```text
ModuleNotFoundError
```

run:

```bash
pip install -r requirements.txt
```

---

## Port Already in Use

If port `5000` is already being used, stop the existing Flask process and run the application again.

---

## Excel File Error

Make sure this file exists:

```text
data/library_books.xlsx
```

The application can initialize the Excel structure if the file does not already exist.

---

## Book Cover Not Displaying

Check:

```text
uploads/book_covers/
```

and verify that the uploaded image is one of:

```text
.png
.jpg
.jpeg
.webp
```

and is not larger than:

```text
5 MB
```

---

# Development Notes

This project currently uses Excel as its data store to keep the system simple,
portable and beginner-friendly.

For a larger production library system, the Excel layer can later be replaced
with:

- SQLite
- PostgreSQL
- MySQL
- MongoDB

without changing the overall frontend concept.

---

# Future Improvements

Possible future modules include:

- 👤 Student/member management
- 📖 Book issue and return
- 📅 Due-date management
- 🔔 Overdue notifications
- 💰 Fine calculation
- 📧 Email notifications
- 📊 Advanced reports
- 📈 Library analytics
- 🧾 PDF reports
- 🔍 Advanced filtering
- 👥 Multiple librarian accounts
- 🔐 Role-based access control
- 🗄️ Database migration
- 📱 Mobile-friendly enhancements
- 📚 Book recommendation system

---

# Educational Purpose

This project is designed as an academic and practical software project for
learning:

- Python
- Flask
- HTML
- CSS
- JavaScript
- Excel automation
- File uploads
- CRUD operations
- REST-style APIs
- Web application deployment

---

# Institution

**B.S. Abdur Rahman Crescent Institute of Science and Technology**

**Crescent College Central Library**

---

## License

This project is intended for educational and academic use.
