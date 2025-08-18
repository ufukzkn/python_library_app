from .library import Library
from .models import Book

def prompt(msg: str) -> str:
    try:
        return input(msg).strip()
    except EOFError:
        return ""

def add_flow(lib: Library) -> None:
    title = prompt("Title: ")
    author = prompt("Author: ")
    isbn = prompt("ISBN: ")
    ok = lib.add_book(Book(title=title, author=author, isbn=isbn))
    print("Added." if ok else "This ISBN already exists!")

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
[1] Add
[2] Remove
[3] List
[4] Find by ISBN
[0] Exit
"""
    while True:
        print(menu)
        c = prompt("Choose: ")
        if c == "1": add_flow(lib)
        elif c == "2": remove_flow(lib)
        elif c == "3": list_flow(lib)
        elif c == "4": search_flow(lib)
        elif c == "0": break
        else: print("Invalid.")

if __name__ == "__main__":
    main()
