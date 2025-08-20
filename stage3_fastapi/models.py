from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union, Optional
from pydantic import BaseModel, Field, ConfigDict

@dataclass
class Book:
    isbn: str  # benzersiz kimlik
    title: str
    authors: List[str]  # API'den gelen yazar listesi
    is_borrowed: bool = False  # Stage 1'de şart değil ama dursun (ileriye dönük)

    def __init__(self, isbn: str, title: str, authors: Union[str, List[str]], is_borrowed: bool = False):
        """
        Stage 1 uyumluluğu için author (string) ve authors (list) destekler
        """
        self.isbn = isbn
        self.title = title
        self.is_borrowed = is_borrowed
        
        if isinstance(authors, str):
            # Stage 1 uyumluluğu: tek string author
            self.authors = [authors]
        else:
            # Stage 2: authors listesi
            self.authors = authors if authors else []

    @property
    def author(self) -> str:
        """Stage 1 uyumluluğu için author property"""
        return self.authors[0] if self.authors else "Unknown Author"

    def __str__(self) -> str:
        # "Ulysses by James Joyce (ISBN: 978-0199535675)" formatı
        authors_str = ", ".join(self.authors) if self.authors else "Unknown Author"
        return f"{self.title} by {authors_str} (ISBN: {self.isbn})"

    def borrow_book(self) -> None:
        if self.is_borrowed:
            raise ValueError(f"'{self.title}' is already borrowed.")
        self.is_borrowed = True

    def return_book(self) -> None:
        if not self.is_borrowed:
            raise ValueError(f"'{self.title}' was not borrowed.")
        self.is_borrowed = False


# FastAPI için Pydantic modelleri
class ISBNRequest(BaseModel):
    """Request model for adding a book by ISBN"""
    isbn: str = Field(..., min_length=10, max_length=17, description="ISBN to fetch from Open Library")

class BookResponse(BaseModel):
    """Response model for book data"""
    isbn: str
    title: str
    authors: List[str]
    is_borrowed: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
