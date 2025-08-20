from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Iterable, Optional
from stage1_oop.models import Book


class Library:
    def __init__(self, filename: str = "library.json") -> None:
        self.filename = filename  # gereksinime göre dosya adı dışarıdan gelir
        self._books: list[Book] = []
        self.load_books()

    # ---------- Kalıcılık ----------
    @property
    def _db_path(self) -> Path:
        return Path(__file__).with_name(self.filename)

    def load_books(self) -> None:
        """library.json dosyasından kitapları yükler."""
        path = self._db_path
        if not path.exists():
            self._books = []
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(data, list)
        except Exception:
            data = []
        self._books = [
            Book(
                title=row.get("title", ""),
                author=row.get("author", ""),
                isbn=row.get("isbn", ""),
                is_borrowed=row.get("is_borrowed", False),
            )
            for row in data
        ]

    def save_books(self) -> None:
        """Mevcut kitap listesini JSON'a yazar."""
        rows: list[dict[str, Any]] = [
            {
                "title": b.title,
                "author": b.author,
                "isbn": b.isbn,
                "is_borrowed": b.is_borrowed,
            }
            for b in self._books
        ]
        self._db_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ---------- Operasyonlar ----------
    def add_book(self, book: Book) -> bool:
        """Yeni bir Book ekler ve dosyayı günceller."""
        if any(b.isbn == book.isbn for b in self._books):
            return False
        self._books.append(book)
        self.save_books()
        return True

    def remove_book(self, isbn: str) -> bool:
        """ISBN'e göre kitabı siler ve dosyayı günceller."""
        for i, b in enumerate(self._books):
            if b.isbn == isbn:
                self._books.pop(i)
                self.save_books()
                return True
        return False

    def list_books(self) -> Iterable[Book]:
        """Tüm kitapları listeler (kopya döndürmek istersen list(...) yap)."""
        return list(self._books)

    def find_book(self, isbn: str) -> Optional[Book]:
        """ISBN ile belirli kitabı döndürür."""
        for b in self._books:
            if b.isbn == isbn:
                return b
        return None
