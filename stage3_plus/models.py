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
    book_type: str = "Physical"  # Physical, Digital, Audio
    
    # Physical book fields
    shelf_location: Optional[str] = None
    
    # Digital book fields
    file_size_mb: Optional[float] = None
    file_format: Optional[str] = None
    
    # Audio book fields
    duration_minutes: Optional[int] = None
    narrator: Optional[str] = None

    def __init__(self, isbn: str, title: str, authors: Union[str, List[str]], 
                 is_borrowed: bool = False, book_type: str = "Physical", **kwargs):
        """
        Stage 1 uyumluluğu için author (string) ve authors (list) destekler
        Enhanced with book types and additional fields
        """
        self.isbn = isbn
        self.title = title
        self.is_borrowed = is_borrowed
        self.book_type = book_type
        
        # Handle authors (backward compatibility)
        if isinstance(authors, str):
            # Stage 1 uyumluluğu: tek string author
            self.authors = [authors]
        else:
            # Stage 2: authors listesi
            self.authors = authors if authors else []
        
        # Set optional fields from kwargs
        self.shelf_location = kwargs.get('shelf_location', None)
        self.file_size_mb = kwargs.get('file_size_mb', None)
        self.file_format = kwargs.get('file_format', None)
        self.duration_minutes = kwargs.get('duration_minutes', None)
        self.narrator = kwargs.get('narrator', None)

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
    book_type: Optional[str] = Field("Physical", description="Type of book: Physical, Digital, or Audio")
    shelf_location: Optional[str] = Field(None, description="Shelf location for physical books")
    file_size_mb: Optional[float] = Field(None, description="File size in MB for digital books")
    file_format: Optional[str] = Field(None, description="File format for digital books")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes for audio books")
    narrator: Optional[str] = Field(None, description="Narrator for audio books")

class BookUpdateRequest(BaseModel):
    """Request model for updating a book"""
    title: Optional[str] = Field(None, min_length=1, description="New title for the book")
    authors: Optional[List[str]] = Field(None, min_items=1, description="New authors list for the book")
    is_borrowed: Optional[bool] = Field(None, description="New borrowed status for the book")
    book_type: Optional[str] = Field(None, pattern="^(Physical|Digital|Audio)$", description="Book type")
    
    # Physical book fields
    shelf_location: Optional[str] = Field(None, description="Shelf location for physical books")
    
    # Digital book fields
    file_size_mb: Optional[float] = Field(None, ge=0, description="File size in MB for digital books")
    file_format: Optional[str] = Field(None, description="File format for digital books")
    
    # Audio book fields
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duration in minutes for audio books")
    narrator: Optional[str] = Field(None, description="Narrator for audio books")

class BookResponse(BaseModel):
    """Response model for book data"""
    isbn: str
    title: str
    authors: List[str]
    is_borrowed: bool = False
    book_type: str = "Physical"
    
    # Optional fields for different book types
    shelf_location: Optional[str] = None
    file_size_mb: Optional[float] = None
    file_format: Optional[str] = None
    duration_minutes: Optional[int] = None
    narrator: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ManualBookRequest(BaseModel):
    """Request model for manually adding a book"""
    isbn: str = Field(..., description="ISBN of the book")
    title: str = Field(..., min_length=1, description="Title of the book")
    authors: List[str] = Field(..., description="List of authors")
    book_type: Optional[str] = Field("Physical", description="Type of book: Physical, Digital, or Audio")
    shelf_location: Optional[str] = Field(None, description="Shelf location for physical books")
    file_size_mb: Optional[float] = Field(None, description="File size in MB for digital books")
    file_format: Optional[str] = Field(None, description="File format for digital books")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes for audio books")
    narrator: Optional[str] = Field(None, description="Narrator for audio books")

class BorrowRequest(BaseModel):
    """Request model for borrowing/returning books"""
    action: str = Field(..., description="Action: 'borrow' or 'return'")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
