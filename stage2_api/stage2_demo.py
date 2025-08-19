#!/usr/bin/env python3
"""
Stage 2 Demo - API Integration with Open Library
Demonstrates both Stage 1 compatibility and Stage 2 new features
"""

from .library import Library
from .models import Book

def demo_stage1_compatibility():
    """Demonstrate Stage 1 style - manual book addition"""
    print("=== Stage 1 Compatibility Demo ===")
    lib = Library("stage1_demo.json")
    
    # Manual book addition (Stage 1 style)
    book1 = Book("978-0345339683", "The Hobbit", "J.R.R. Tolkien")
    result = lib.add_book(book1)
    print(f"Manual addition result: {result}")
    
    # List books
    print("Books in library:")
    for book in lib.list_books():
        print(f"  - {book}")
    print()

def demo_stage2_api():
    """Demonstrate Stage 2 API integration"""
    print("=== Stage 2 API Integration Demo ===")
    lib = Library("stage2_demo.json")
    
    # API-based book addition (Stage 2 style)
    test_isbns = [
        "9780140328721",  # Fantastic Mr. Fox by Roald Dahl
        "9780747532699",  # Harry Potter (UK edition)
        "9780345339683",  # The Hobbit (duplicate test)
    ]
    
    for isbn in test_isbns:
        print(f"Adding book with ISBN: {isbn}")
        result = lib.add_book(isbn)
        print(f"Result: {result}")
        print()
    
    # List all books
    print("All books in library:")
    for i, book in enumerate(lib.list_books(), 1):
        print(f"  {i}. {book}")
        print(f"     Authors: {', '.join(book.authors)}")
        print(f"     Borrowed: {book.is_borrowed}")
    print()

def demo_error_handling():
    """Demonstrate error handling"""
    print("=== Error Handling Demo ===")
    lib = Library("error_demo.json")
    
    # Test with invalid ISBN
    print("Testing invalid ISBN...")
    result = lib.add_book("0000000000000")
    print(f"Invalid ISBN result: {result}")
    print()

def main():
    print("Python Library Management System - Stage 2 Demo")
    print("=" * 50)
    print()
    
    demo_stage1_compatibility()
    demo_stage2_api()
    demo_error_handling()
    
    print("Demo completed!")

if __name__ == "__main__":
    main()
