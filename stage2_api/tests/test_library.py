from pathlib import Path

def test_add_list_find_remove(tmp_path, monkeypatch):
    # library.Library içindeki dosya adını geçici dosyayla değiştir
    import stage1_oop.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage1_oop.library import Library
    from stage1_oop.models import Book

    lib = Library()  # filename default
    assert list(lib.list_books()) == []

    b1 = Book("The Hobbit", "J.R.R. Tolkien", "978-0345339683")
    assert lib.add_book(b1) is True
    assert lib.add_book(b1) is False  # aynı ISBN eklenemez

    # list_books
    books = list(lib.list_books())
    assert len(books) == 1 and books[0].isbn == "978-0345339683"

    # find_book
    found = lib.find_book("978-0345339683")
    assert found is not None and found.title == "The Hobbit"

    # remove_book
    assert lib.remove_book("978-0345339683") is True
    assert lib.find_book("978-0345339683") is None
