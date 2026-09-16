# Crescent College Library Management System

A professional web-based Library Book Management System developed for the
B.S. Abdur Rahman Crescent Institute of Science and Technology.

The system is designed to help library staff manage the college book
catalog efficiently through a simple web interface.

---

## Project Overview

The Crescent College Library Management System provides a centralized
platform for managing library books and their details.

The librarian can:

- Add new books
- Upload book-cover images
- Store book information in Excel
- View all books
- Search the library catalog
- View individual book details
- Edit book information
- Update book-cover images
- Delete books
- Track total copies
- Track available copies
- Track borrowed copies
- View basic library statistics

The system is designed with a modular architecture so that additional
library features can be added in future versions.

---

## Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Google Fonts

### Backend

- Python
- Flask

### Database / Storage

- Microsoft Excel (.xlsx)
- openpyxl

### Image Processing

- Pillow

### Deployment

- Gunicorn
- WSGI

---

## Main Features

### 1. Librarian Dashboard

The dashboard provides an overview of the library collection.

It displays:

- Total books
- Total copies
- Available copies
- Borrowed copies
- Recently added books
- Quick actions

---

### 2. Add Book

The librarian can enter:

- Book ID
- Book title
- Author
- ISBN
- Category
- Publisher
- Publication year
- Number of copies
- Shelf number
- Book cover

When a book is added:

1. A unique book record is created.
2. The cover image is validated.
3. The cover image is stored securely.
4. The book information is stored in Excel.
5. The book becomes available in the library catalog.

---

### 3. Book Cover Management

The system supports:

- PNG
- JPG
- JPEG
- WEBP

Maximum upload size:

5 MB

Uploaded images are stored in:

uploads/book_covers/

The Excel file stores the image filename rather than storing the image
inside the spreadsheet.

---

### 4. Book Catalog

The librarian can view all books in the library catalog.

The catalog provides:

- Book cover
- Title
- Author
- Category
- ISBN
- Copy availability
- Shelf location

---

### 5. Search

Books can be searched using:

- Book ID
- Title
- Author
- ISBN
- Category
- Publisher
- Shelf number

---

### 6. Edit Book

The librarian can update:

- Book title
- Author
- ISBN
- Category
- Publisher
- Publication year
- Total copies
- Shelf number
- Book cover

The system preserves the number of currently borrowed copies when
the total number of copies is modified.

---

### 7. Delete Book

Books can be removed from the catalog.

The system prevents deletion when copies of the book are currently
borrowed.

The associated cover image is also removed after successful deletion.

---

## Project Structure

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
