from __future__ import annotations
from pathlib import Path
import json
import httpx
from typing import Any, Iterable, Optional, List
from models import Book

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
        
        self._books = []
        for row in data:
            # Stage 1 uyumluluğu: author ve authors alanlarını destekle
            if "authors" in row:
                authors = row["authors"]
            elif "author" in row:
                authors = [row["author"]]
            else:
                authors = []
            
            book = Book(
                isbn=row.get("isbn", ""),
                title=row.get("title", ""),
                authors=authors,
                is_borrowed=row.get("is_borrowed", False),
            )
            self._books.append(book)

    def save_books(self) -> None:
        """Mevcut kitap listesini JSON'a yazar."""
        rows: list[dict[str, Any]] = [
            {
                "isbn": b.isbn,
                "title": b.title,
                "authors": b.authors,
                "author": b.author,  # Stage 1 uyumluluğu için
                "is_borrowed": b.is_borrowed,
            }
            for b in self._books
        ]
        self._db_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ---------- API İşlemleri ----------
    def fetch_book_from_api(self, isbn: str) -> Optional[Book]:
        """Open Library API'sinden ISBN ile kitap bilgilerini çeker."""
        try:
            # ISBN ile kitap bilgilerini çek
            response = httpx.get(f"https://openlibrary.org/isbn/{isbn}.json", timeout=10.0, follow_redirects=True)
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            
            try:
                data = response.json()
            except (ValueError, Exception):
                # JSON parsing hatası
                return None
            
            title = data.get("title")
            if not title:
                return None
            
            # Yazar bilgilerini çek
            authors: List[str] = []
            if data.get("authors"):
                for author_ref in data["authors"]:
                    if isinstance(author_ref, dict) and author_ref.get("key"):
                        try:
                            author_response = httpx.get(f"https://openlibrary.org{author_ref['key']}.json", timeout=10.0, follow_redirects=True)
                            author_response.raise_for_status()
                            author_data = author_response.json()
                            if author_data.get("name"):
                                authors.append(author_data["name"])
                        except (httpx.HTTPError, httpx.RequestError, ValueError, Exception):
                            # Yazar bilgisi çekilemezse atla
                            continue
            
            # Eğer yazar bulunamazsa by_statement'ı kullan
            if not authors and data.get("by_statement"):
                authors = [data["by_statement"]]
            
            return Book(isbn=isbn, title=title, authors=authors)
            
        except httpx.RequestError:
            # Ağ hatası
            return None
        except httpx.HTTPStatusError:
            # HTTP hatası
            return None
        except Exception:
            # Diğer beklenmeyen hatalar
            return None

    # ---------- Operasyonlar ----------
    def add_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """ISBN ile kitap ekler - API'den bilgileri çeker (Stage 2 özelliği)."""
        # Kitap zaten var mı kontrol et
        if any(b.isbn == isbn for b in self._books):
            print("Book with this ISBN already exists.")
            return None
        
        # API'den kitap bilgilerini çek
        book = self.fetch_book_from_api(isbn)
        if book is None:
            print("Book not found.")
            return None
        
        self._books.append(book)
        self.save_books()
        print(f"Book added: {book}")
        return book

    def add_book(self, book_or_isbn) -> bool:
        """
        Stage 1 uyumluluğu: Book objesi kabul eder
        Stage 2 özelliği: String ISBN de kabul eder
        """
        if isinstance(book_or_isbn, str):
            # Stage 2: ISBN string
            result = self.add_book_by_isbn(book_or_isbn)
            return result is not None
        else:
            # Stage 1: Book object
            book = book_or_isbn
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
        """Tüm kitapları listeler."""
        return list(self._books)

    def find_book(self, isbn: str) -> Optional[Book]:
        """ISBN ile belirli kitabı döndürür."""
        for b in self._books:
            if b.isbn == isbn:
                return b
        return None
