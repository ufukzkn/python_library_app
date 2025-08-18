from stage1_oop.models import Book
import pytest

def test_remove_nonexistent(tmp_path, monkeypatch):
    import stage1_oop.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage1_oop.library import Library

    lib = Library()
    # olmayan ISBN silmeye çalış
    assert lib.remove_book("not-here") is False

def test_find_nonexistent(tmp_path, monkeypatch):
    import stage1_oop.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage1_oop.library import Library
    lib = Library()
    assert lib.find_book("not-here") is None

def test_persistence_between_instances(tmp_path, monkeypatch):
    import stage1_oop.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage1_oop.library import Library
    from stage1_oop.models import Book

    lib1 = Library()
    lib1.add_book(Book("1984", "George Orwell", "978-0451524935"))

    # yeni Library açınca JSON’dan yüklenmeli
    lib2 = Library()
    assert lib2.find_book("978-0451524935") is not None
    