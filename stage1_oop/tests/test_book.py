import pytest
from stage1_oop.models import Book

def test_book_str_format():
    b = Book("Ulysses", "James Joyce", "978-0199535675")
    assert str(b) == "Ulysses by James Joyce (ISBN: 978-0199535675)"

def test_borrow_and_return():
    b = Book("Dune", "Frank Herbert", "978-0441013593")
    assert b.is_borrowed is False

    b.borrow_book()
    assert b.is_borrowed is True

    b.return_book()
    assert b.is_borrowed is False

def test_double_borrow_raises():
    b = Book("Clean Code", "Robert C. Martin", "978-0132350884")
    b.borrow_book()
    with pytest.raises(ValueError):
        b.borrow_book()

def test_double_return_raises():
    b = Book("Refactoring", "Martin Fowler", "978-0201485677")
    with pytest.raises(ValueError):
        b.return_book()
