from pathlib import Path
import httpx

class FakeResponse:
    def __init__(self, status_code=200, data=None, url="https://example.com"):
        self.status_code = status_code
        self._data = data or {}
        self.url = url
        self.headers = {}

    def json(self):
        return self._data

    def raise_for_status(self):
        if 400 <= self.status_code:
            request = httpx.Request("GET", self.url)
            raise httpx.HTTPStatusError("HTTP error", request=request, response=self)

def test_stage1_compatibility(tmp_path, monkeypatch):
    """Test Stage 1 compatibility - manual book addition"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage2_api.library import Library
    from stage2_api.models import Book

    lib = Library()
    assert list(lib.list_books()) == []

    # Stage 1 style: Book object with author string
    b1 = Book("978-0345339683", "The Hobbit", "J.R.R. Tolkien")
    assert lib.add_book(b1) is True
    assert lib.add_book(b1) is False  # aynı ISBN eklenemez

    # list_books
    books = list(lib.list_books())
    assert len(books) == 1 and books[0].isbn == "978-0345339683"
    assert books[0].author == "J.R.R. Tolkien"  # Stage 1 uyumluluğu

    # find_book
    found = lib.find_book("978-0345339683")
    assert found is not None and found.title == "The Hobbit"

    # remove_book
    assert lib.remove_book("978-0345339683") is True
    assert lib.find_book("978-0345339683") is None

def test_stage2_api_functionality(tmp_path, monkeypatch):
    """Test Stage 2 API functionality"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage2_api.library import Library
    from stage2_api.models import Book

    # Mock API response
    def mock_get(url, timeout=10.0, follow_redirects=True):
        if "isbn/9780143127741" in url:
            class MockResponse:
                status_code = 200
                def json(self):
                    return {
                        "title": "Sapiens",
                        "authors": [{"key": "/authors/OL1394243A"}]
                    }
                def raise_for_status(self):
                    pass
            return MockResponse()
        elif "authors/OL1394243A" in url:
            class MockResponse:
                status_code = 200
                def json(self):
                    return {"name": "Yuval Noah Harari"}
                def raise_for_status(self):
                    pass
            return MockResponse()
        else:
            class MockResponse:
                status_code = 404
                def raise_for_status(self):
                    raise httpx.HTTPStatusError("404", request=None, response=self)
            return MockResponse()
    
    monkeypatch.setattr(httpx, "get", mock_get)

    lib = Library()
    assert list(lib.list_books()) == []

    # Test API ile kitap ekleme (Stage 2 style)
    result = lib.add_book("9780143127741")  # ISBN string
    assert result is True
    
    books = list(lib.list_books())
    assert len(books) == 1
    book = books[0]
    assert book.isbn == "9780143127741"
    assert book.title == "Sapiens"
    assert "Yuval Noah Harari" in book.authors

def test_api_book_not_found(tmp_path, monkeypatch, capsys):
    """Test when API returns 404 for ISBN"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    def mock_get(url, timeout=10.0, follow_redirects=True):
        class MockResponse:
            status_code = 404
            def raise_for_status(self):
                raise httpx.HTTPStatusError("404", request=None, response=self)
        return MockResponse()
    
    monkeypatch.setattr(httpx, "get", mock_get)

    from stage2_api.library import Library
    
    lib = Library()
    result = lib.add_book("0000000000000")
    
    captured = capsys.readouterr()
    assert result is False
    assert "Book not found." in captured.out
    assert len(list(lib.list_books())) == 0

def test_api_network_error(tmp_path, monkeypatch, capsys):
    """Test when network error occurs"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    def mock_get(url, timeout=10.0, follow_redirects=True):
        raise httpx.RequestError("Network error")
    
    monkeypatch.setattr(httpx, "get", mock_get)

    from stage2_api.library import Library
    
    lib = Library()
    result = lib.add_book("9780143127741")
    
    captured = capsys.readouterr()
    assert result is False
    assert "Book not found." in captured.out  # Network hatası da aynı mesajı verir
    assert len(list(lib.list_books())) == 0

def test_api_malformed_json(tmp_path, monkeypatch, capsys):
    """Test malformed JSON response from API"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    def mock_get(url, timeout=10.0, follow_redirects=True):
        class BadResponse:
            status_code = 200
            def json(self):
                raise ValueError("Invalid JSON")
            def raise_for_status(self):
                pass
        return BadResponse()
    
    monkeypatch.setattr(httpx, "get", mock_get)

    from stage2_api.library import Library
    
    lib = Library()
    result = lib.add_book("9780140328721")
    
    captured = capsys.readouterr()
    assert result is False
    assert "Book not found." in captured.out
    assert len(list(lib.list_books())) == 0

def test_api_missing_title(tmp_path, monkeypatch, capsys):
    """Test API response with missing title"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    def mock_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {"authors": [{"key": "/authors/OL34184A"}]})
        return FakeResponse(200, {"name": "Test Author"})
    
    monkeypatch.setattr(httpx, "get", mock_get)

    from stage2_api.library import Library
    
    lib = Library()
    result = lib.add_book("9780140328721")
    
    captured = capsys.readouterr()
    assert result is False
    assert "Book not found." in captured.out
    assert len(list(lib.list_books())) == 0

def test_api_empty_response(tmp_path, monkeypatch, capsys):
    """Test API empty response"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    def mock_get(url, timeout=10.0, follow_redirects=True):
        return FakeResponse(200, {})
    
    monkeypatch.setattr(httpx, "get", mock_get)

    from stage2_api.library import Library
    
    lib = Library()
    result = lib.add_book("9780140328721")
    
    captured = capsys.readouterr()
    assert result is False
    assert "Book not found." in captured.out
    assert len(list(lib.list_books())) == 0

def test_mixed_operations(tmp_path, monkeypatch):
    """Test mixing Stage 1 and Stage 2 operations"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage2_api.library import Library
    from stage2_api.models import Book

    def mock_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "API Book",
                "authors": [{"key": "/authors/OL123A"}]
            })
        return FakeResponse(200, {"name": "API Author"})
    
    monkeypatch.setattr(httpx, "get", mock_get)

    lib = Library()
    
    # Stage 1: Manual add
    manual_book = Book("1111111111111", "Manual Book", "Manual Author")
    assert lib.add_book(manual_book) is True
    
    # Stage 2: API add
    assert lib.add_book("9780140328721") is True
    
    # Verify both books exist
    books = list(lib.list_books())
    assert len(books) == 2
    
    titles = [book.title for book in books]
    assert "Manual Book" in titles
    assert "API Book" in titles

def test_duplicate_isbn_different_sources(tmp_path, monkeypatch, capsys):
    """Test adding same ISBN via Stage 1 and Stage 2"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage2_api.library import Library
    from stage2_api.models import Book

    def mock_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "API Version",
                "authors": [{"key": "/authors/OL123A"}]
            })
        return FakeResponse(200, {"name": "API Author"})
    
    monkeypatch.setattr(httpx, "get", mock_get)

    lib = Library()
    
    # Add manually first
    manual_book = Book("9780140328721", "Manual Version", "Manual Author")
    assert lib.add_book(manual_book) is True
    
    # Try to add same ISBN via API
    result = lib.add_book("9780140328721")
    captured = capsys.readouterr()
    assert result is False  # Should reject duplicate
    assert "Book with this ISBN already exists." in captured.out
    
    # Verify only one book exists with manual data
    books = list(lib.list_books())
    assert len(books) == 1
    assert books[0].title == "Manual Version"

def test_api_author_fetch_failure(tmp_path, monkeypatch):
    """Test when book data is fetched but author fetch fails"""
    import stage2_api.library as libmod
    monkeypatch.setattr(libmod.Library, "_db_path", property(lambda self: tmp_path / "lib.json"))

    from stage2_api.library import Library

    def mock_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "Test Book",
                "authors": [{"key": "/authors/OL123A"}],
                "by_statement": "Fallback Author"
            })
        else:
            # Author fetch fails
            raise httpx.RequestError("Author fetch failed")
    
    monkeypatch.setattr(httpx, "get", mock_get)

    lib = Library()
    result = lib.add_book("9780140328721")
    
    # Should succeed with fallback author
    assert result is True
    books = list(lib.list_books())
    assert len(books) == 1
    assert books[0].title == "Test Book"
    assert "Fallback Author" in books[0].authors
