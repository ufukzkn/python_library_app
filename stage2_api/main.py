from library import Library
from models import Book

def prompt(msg: str) -> str:
    try:
        return input(msg).strip()
    except EOFError:
        return ""

def add_flow_legacy(lib: Library) -> None:
    """Stage 1 style: Manual entry of all book details."""
    title = prompt("Title: ")
    authors_str = prompt("Author(s) (comma separated): ")
    isbn = prompt("ISBN: ")
    
    authors = [a.strip() for a in authors_str.split(",") if a.strip()]
    if not authors:
        authors = ["Unknown Author"]
    
    book = Book(isbn=isbn, title=title, authors=authors)
    ok = lib.add_book(book)
    print("Added." if ok else "This ISBN already exists!")

def add_flow_api(lib: Library) -> None:
    """Stage 2 style: ISBN-based addition with API lookup."""
    isbn = prompt("ISBN: ")
    if not isbn:
        print("ISBN cannot be empty.")
        return
    
    book = lib.add_book(isbn)
    if book:
        print(f"Book successfully added: {book}")
    # Error messages are already printed by lib.add_book

def remove_flow(lib: Library) -> None:
    isbn = prompt("ISBN to remove: ")
    ok = lib.remove_book(isbn)
    print("Removed." if ok else "Not found.")

def list_flow(lib: Library) -> None:
    books = list(lib.list_books())
    if not books:
        print("(no books)")
        return
    for i, b in enumerate(books, start=1):
        print(f"{i:2d}. {b}")  # __str__ kullanılacak

def search_flow(lib: Library) -> None:
    isbn = prompt("ISBN to find: ")
    book = lib.find_book(isbn)
    print(book if book else "(not found)")

def main() -> None:
    # Dosya adını değiştirmek istersen burada parametre ver:
    lib = Library(filename="library.json")

    menu = """
[1] Add book manually (Stage 1 style)
[2] Add book by ISBN from API (Stage 2 style)
[3] Remove
[4] List
[5] Find by ISBN
[0] Exit
"""
    while True:
        print(menu)
        c = prompt("Choose: ")
        if c == "1": add_flow_legacy(lib)
        elif c == "2": add_flow_api(lib)
        elif c == "3": remove_flow(lib)
        elif c == "4": list_flow(lib)
        elif c == "5": search_flow(lib)
        elif c == "0": break
        else: print("Invalid.")

if __name__ == "__main__":
    main()
