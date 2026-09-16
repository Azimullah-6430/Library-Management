# Crescent College Central Library — AI Book Management System

A Flask-based library management system that registers books by scanning only the **front and back images** of a book.

## Features

- Professional library dashboard
- AI-powered book scanning
- Front and back book image upload
- OCR-based text extraction
- ISBN detection and validation
- AI metadata extraction
- Automatic Book ID generation
- Automatic Excel storage
- Duplicate ISBN detection
- Book catalogue
- Book details page
- Available and borrowed book views
- Search and category filtering
- Book cover image storage
- Responsive professional UI
- Optional Gemini AI integration

## Automatically Extracted Details

The system attempts to detect:

- Book Title
- Author
- Subtitle
- ISBN
- Category
- Publisher
- Publication Year
- Edition
- Price

The following circulation information is generated automatically:

- Total Copies
- Available Copies
- Borrowed Copies
- Date Added
- Book ID
- Scan Status

## Project Structure

```text
library_management_system/
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
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png
│
└── utils/
    ├── __init__.py
    ├── excel_manager.py
    ├── image_manager.py
    ├── book_manager.py
    ├── ocr_manager.py
    └── book_scanner.py
