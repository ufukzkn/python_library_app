"""
Stage 3 FastAPI Tests
"""

import pytest
import httpx
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os
import sys
sys.path.append(str(Path(__file__).parent.parent))

from api import app
from library import Library

# Test client
client = TestClient(app)

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

@pytest.fixture
def temp_library(monkeypatch, tmp_path):
    """Create a temporary library for testing"""
    test_file = tmp_path / "test_api.json"
    
    # Patch the global library instance to use temporary file
    from api import library
    
    # Direct patching of the _db_path property using a different approach
    def mock_db_path(self):
        return test_file
    
    # Patch the method instead of the property
    monkeypatch.setattr(type(library), "_db_path", property(mock_db_path))
    
    # Clear existing books and reload from empty file
    library._books = []
    library.save_books()
    
    return library

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Library Management API" in data["message"]
    assert data["version"] == "3.0.0"
    assert "docs" in data

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_books" in data

def test_list_books_empty(temp_library):
    """Test listing books when library is empty"""
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

def test_add_book_by_isbn_success(temp_library, monkeypatch):
    """Test successfully adding a book by ISBN"""
    isbn = "9780140328721"
    book_url = f"https://openlibrary.org/isbn/{isbn}.json"
    author_key = "/authors/OL34184A"
    author_url = f"https://openlibrary.org{author_key}.json"

    def fake_get(url, timeout=10.0, follow_redirects=True):
        if url == book_url:
            return FakeResponse(200, {
                "title": "Fantastic Mr. Fox",
                "authors": [{"key": author_key}]
            })
        if url == author_url:
            return FakeResponse(200, {"name": "Roald Dahl"})
        return FakeResponse(404, {})

    monkeypatch.setattr(httpx, "get", fake_get)

    response = client.post("/books", json={"isbn": isbn})
    
    assert response.status_code == 201
    data = response.json()
    assert data["isbn"] == isbn
    assert data["title"] == "Fantastic Mr. Fox"
    assert "Roald Dahl" in data["authors"]
    assert data["is_borrowed"] is False

def test_add_book_invalid_isbn(temp_library, monkeypatch):
    """Test adding a book with invalid ISBN"""
    isbn = "0000000000000"
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        return FakeResponse(404, {})

    monkeypatch.setattr(httpx, "get", fake_get)

    response = client.post("/books", json={"isbn": isbn})
    
    assert response.status_code == 400
    assert "Failed to add book" in response.json()["detail"]

def test_add_duplicate_book(temp_library, monkeypatch):
    """Test adding the same book twice"""
    isbn = "9780140328721"
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "Test Book",
                "authors": [{"key": "/authors/OL123A"}]
            })
        return FakeResponse(200, {"name": "Test Author"})

    monkeypatch.setattr(httpx, "get", fake_get)

    # Add book first time
    response1 = client.post("/books", json={"isbn": isbn})
    assert response1.status_code == 201

    # Try to add same book again
    response2 = client.post("/books", json={"isbn": isbn})
    assert response2.status_code == 400
    assert "Failed to add book" in response2.json()["detail"]

def test_get_book_by_isbn(temp_library, monkeypatch):
    """Test getting a specific book by ISBN"""
    isbn = "9780140328721"
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "Test Book",
                "authors": [{"key": "/authors/OL123A"}]
            })
        return FakeResponse(200, {"name": "Test Author"})

    monkeypatch.setattr(httpx, "get", fake_get)

    # First add a book
    client.post("/books", json={"isbn": isbn})

    # Then get it
    response = client.get(f"/books/{isbn}")
    assert response.status_code == 200
    data = response.json()
    assert data["isbn"] == isbn
    assert data["title"] == "Test Book"

def test_get_book_not_found(temp_library):
    """Test getting a non-existent book"""
    response = client.get("/books/9999999999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_book_success(temp_library, monkeypatch):
    """Test successfully deleting a book"""
    isbn = "9780140328721"
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "Test Book",
                "authors": [{"key": "/authors/OL123A"}]
            })
        return FakeResponse(200, {"name": "Test Author"})

    monkeypatch.setattr(httpx, "get", fake_get)

    # First add a book
    client.post("/books", json={"isbn": isbn})

    # Then delete it
    response = client.delete(f"/books/{isbn}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/books/{isbn}")
    assert response.status_code == 404

def test_delete_book_not_found(temp_library):
    """Test deleting a non-existent book"""
    response = client.delete("/books/9999999999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_list_books_with_data(temp_library, monkeypatch):
    """Test listing books when library has data"""
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        if "9780140328721" in url:
            return FakeResponse(200, {
                "title": "Book One",
                "authors": [{"key": "/authors/OL1A"}]
            })
        elif "9780345339683" in url:
            return FakeResponse(200, {
                "title": "Book Two", 
                "authors": [{"key": "/authors/OL2A"}]
            })
        elif "/authors/OL1A" in url:
            return FakeResponse(200, {"name": "Author One"})
        elif "/authors/OL2A" in url:
            return FakeResponse(200, {"name": "Author Two"})
        return FakeResponse(404, {})

    monkeypatch.setattr(httpx, "get", fake_get)

    # Add some books
    client.post("/books", json={"isbn": "9780140328721"})
    client.post("/books", json={"isbn": "9780345339683"})

    # List books
    response = client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 2
    
    titles = [book["title"] for book in books]
    assert "Book One" in titles
    assert "Book Two" in titles

def test_api_workflow(temp_library, monkeypatch):
    """Test complete API workflow: add, list, get, delete"""
    isbn = "9780140328721"
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        if "isbn" in url:
            return FakeResponse(200, {
                "title": "Workflow Test Book",
                "authors": [{"key": "/authors/OL123A"}]
            })
        return FakeResponse(200, {"name": "Workflow Author"})

    monkeypatch.setattr(httpx, "get", fake_get)

    # 1. Start with empty library
    response = client.get("/books")
    assert len(response.json()) == 0

    # 2. Add a book
    response = client.post("/books", json={"isbn": isbn})
    assert response.status_code == 201

    # 3. List books (should have 1)
    response = client.get("/books")
    assert len(response.json()) == 1

    # 4. Get specific book
    response = client.get(f"/books/{isbn}")
    assert response.status_code == 200
    assert response.json()["title"] == "Workflow Test Book"

    # 5. Delete book
    response = client.delete(f"/books/{isbn}")
    assert response.status_code == 204

    # 6. Verify deletion
    response = client.get("/books")
    assert len(response.json()) == 0

def test_invalid_isbn_format():
    """Test adding book with invalid ISBN format"""
    # Too short
    response = client.post("/books", json={"isbn": "123"})
    assert response.status_code == 422
    
    # Empty
    response = client.post("/books", json={"isbn": ""})
    assert response.status_code == 422

def test_missing_isbn_field():
    """Test adding book without ISBN field"""
    response = client.post("/books", json={})
    assert response.status_code == 422

def test_network_error_handling(temp_library, monkeypatch):
    """Test network error handling"""
    
    def fake_get(url, timeout=10.0, follow_redirects=True):
        raise httpx.RequestError("Network error", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)

    response = client.post("/books", json={"isbn": "9780140328721"})
    assert response.status_code == 400
    assert "Failed to add book" in response.json()["detail"]
