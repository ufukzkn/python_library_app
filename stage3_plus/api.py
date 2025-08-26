"""
Stage 3: FastAPI Web API
Kütüphane yönetim sistemi için REST API
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
import os

from stage3_fastapi.library import Library
from stage3_fastapi.models import ISBNRequest, BookResponse, BookUpdateRequest, ErrorResponse, ManualBookRequest, Book, BorrowRequest

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="Library Management API",
    description="Stage 3: Kütüphane yönetim sistemi REST API'si. Open Library entegrasyonu ile ISBN'den otomatik kitap ekleme.",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (HTML/CSS/JS frontend)
# Get the static directory path relative to the current working directory
static_path = os.path.join("stage3_fastapi", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
else:
    logger.warning(f"Static directory not found: {static_path}")

# Global library instance
library = Library("library.json")  # library_api.json yerine

@app.get("/", tags=["Root"])
async def root():
    """API ana sayfa"""
    frontend_available = os.path.exists(os.path.join("stage3_fastapi", "static", "index.html"))
    
    response_data = {
        "message": "Library Management API - Stage 3",
        "version": "3.0.0",
        "features": ["Open Library Integration", "ISBN-based book addition", "Full CRUD operations"],
        "docs": "/docs",
        "redoc": "/redoc"
    }
    
    if frontend_available:
        response_data["features"].append("Web Frontend")
        response_data["frontend"] = "/static/index.html"
    
    return response_data

@app.get("/books", response_model=List[BookResponse], tags=["Books"])
async def list_books():
    """
    Kütüphanedeki tüm kitapları listele
    
    Returns:
        List[BookResponse]: Tüm kitapların listesi
    """
    try:
        books = list(library.list_books())
        logger.info(f"Listed {len(books)} books")
        return [BookResponse(**vars(book)) for book in books]
    except Exception as e:
        logger.error(f"Error listing books: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve books"
        )

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def add_book(payload: ISBNRequest):
    """
    ISBN ile Open Library'den kitap bilgilerini çekerek kütüphaneye ekle
    
    Args:
        payload (ISBNRequest): ISBN ve kitap tipi içeren istek
        
    Returns:
        BookResponse: Eklenen kitap bilgileri
        
    Raises:
        HTTPException: Kitap eklenemediğinde (geçersiz ISBN, ağ hatası, vs.)
    """
    try:
        logger.info(f"Adding book with ISBN: {payload.isbn}, Type: {payload.book_type}")
        
        # Extra fields'i hazırla
        extra_fields = {}
        if payload.shelf_location:
            extra_fields['shelf_location'] = payload.shelf_location
        if payload.file_size_mb:
            extra_fields['file_size_mb'] = payload.file_size_mb
        if payload.file_format:
            extra_fields['file_format'] = payload.file_format
        if payload.duration_minutes:
            extra_fields['duration_minutes'] = payload.duration_minutes
        if payload.narrator:
            extra_fields['narrator'] = payload.narrator
        
        # ISBN ile kitap ekleme (güncellenmiş fonksiyon)
        result = library.add_book_by_isbn(payload.isbn, payload.book_type or "Physical", **extra_fields)
        
        if not result:
            logger.warning(f"Failed to add book with ISBN: {payload.isbn}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add book. ISBN may be invalid, book already exists, or network error occurred."
            )
        
        # Eklenen kitabı bul ve döndür
        book = library.find_book(payload.isbn)
        if not book:
            logger.error(f"Book added but not found: {payload.isbn}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Book was added but could not be retrieved"
            )
        
        logger.info(f"Successfully added book: {book.title}")
        return BookResponse(**vars(book))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the book"
        )

@app.post("/books/manual", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def add_manual_book(payload: ManualBookRequest):
    """
    Manuel olarak kitap bilgilerini girerek kütüphaneye ekle
    
    Args:
        payload (ManualBookRequest): Kitap bilgileri
        
    Returns:
        BookResponse: Eklenen kitap bilgileri
        
    Raises:
        HTTPException: Kitap eklenemediğinde (ISBN zaten mevcut, vs.)
    """
    try:
        logger.info(f"Adding manual book: {payload.title} by {', '.join(payload.authors)}")
        
        # Basic validation
        if not payload.authors or len(payload.authors) == 0 or all(not author.strip() for author in payload.authors):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one author is required"
            )
        
        # Clean authors list
        clean_authors = [author.strip() for author in payload.authors if author.strip()]
        
        # Kitabın zaten var olup olmadığını kontrol et
        existing_book = library.find_book(payload.isbn)
        if existing_book:
            logger.warning(f"Book with ISBN {payload.isbn} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {payload.isbn} already exists"
            )
        
        # Manuel kitap objesi oluştur
        book_data = {
            'isbn': payload.isbn,
            'title': payload.title,
            'authors': clean_authors,
            'book_type': payload.book_type or 'Physical'
        }
        
        # Book type'a göre ek alanları ekle
        if payload.book_type == 'Physical' and payload.shelf_location:
            book_data['shelf_location'] = payload.shelf_location
        elif payload.book_type == 'Digital':
            if payload.file_size_mb:
                book_data['file_size_mb'] = payload.file_size_mb
            if payload.file_format:
                book_data['file_format'] = payload.file_format
        elif payload.book_type == 'Audio':
            if payload.duration_minutes:
                book_data['duration_minutes'] = payload.duration_minutes
            if payload.narrator:
                book_data['narrator'] = payload.narrator
        
        book = Book(**book_data)
        
        # Kitabı kütüphaneye ekle (Library.add_book metodunu kullan)
        success = library.add_book(book)
        if not success:
            logger.warning(f"Failed to add book to library: {book.title}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add book to library"
            )
        
        logger.info(f"Successfully added manual book: {book.title}")
        return BookResponse(**vars(book))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding manual book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the manual book"
        )

@app.delete("/books/{isbn}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
async def delete_book(isbn: str):
    """
    Belirtilen ISBN'e sahip kitabı kütüphaneden sil
    
    Args:
        isbn (str): Silinecek kitabın ISBN'i
        
    Raises:
        HTTPException: Kitap bulunamadığında 404 hatası
    """
    try:
        logger.info(f"Deleting book with ISBN: {isbn}")
        
        # Kitabı sil
        result = library.remove_book(isbn)
        
        if not result:
            logger.warning(f"Book not found for deletion: {isbn}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ISBN {isbn} not found"
            )
        
        logger.info(f"Successfully deleted book with ISBN: {isbn}")
        return  # 204 No Content response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the book"
        )

@app.get("/books/{isbn}", response_model=BookResponse, tags=["Books"])
async def get_book(isbn: str):
    """
    Belirtilen ISBN'e sahip kitabı getir
    
    Args:
        isbn (str): Aranacak kitabın ISBN'i
        
    Returns:
        BookResponse: Bulunan kitap bilgileri
        
    Raises:
        HTTPException: Kitap bulunamadığında 404 hatası
    """
    try:
        logger.info(f"Getting book with ISBN: {isbn}")
        
        book = library.find_book(isbn)
        
        if not book:
            logger.warning(f"Book not found: {isbn}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ISBN {isbn} not found"
            )
        
        logger.info(f"Found book: {book.title}")
        return BookResponse(**vars(book))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the book"
        )

@app.put("/books/{isbn}", response_model=BookResponse, tags=["Books"])
async def update_book(isbn: str, payload: BookUpdateRequest):
    """
    Belirtilen ISBN'e sahip kitabın bilgilerini güncelle
    
    Args:
        isbn (str): Güncellenecek kitabın ISBN'i
        payload (BookUpdateRequest): Güncellenecek alanlar
        
    Returns:
        BookResponse: Güncellenmiş kitap bilgileri
        
    Raises:
        HTTPException: Kitap bulunamadığında 404 hatası
    """
    try:
        logger.info(f"Updating book with ISBN: {isbn}")
        
        # Kitabın var olup olmadığını kontrol et
        book = library.find_book(isbn)
        if not book:
            logger.warning(f"Book not found for update: {isbn}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ISBN {isbn} not found"
            )
        
        # Sadece belirtilen alanları güncelle
        if payload.title is not None:
            book.title = payload.title
            logger.info(f"Updated title to: {payload.title}")
            
        if payload.authors is not None:
            book.authors = payload.authors
            logger.info(f"Updated authors to: {payload.authors}")
            
        if payload.is_borrowed is not None:
            book.is_borrowed = payload.is_borrowed
            logger.info(f"Updated borrowed status to: {payload.is_borrowed}")
            
        if payload.book_type is not None:
            book.book_type = payload.book_type
            logger.info(f"Updated book type to: {payload.book_type}")
            
        # Physical book fields
        if payload.shelf_location is not None:
            book.shelf_location = payload.shelf_location
            logger.info(f"Updated shelf location to: {payload.shelf_location}")
            
        # Digital book fields
        if payload.file_size_mb is not None:
            book.file_size_mb = payload.file_size_mb
            logger.info(f"Updated file size to: {payload.file_size_mb}")
            
        if payload.file_format is not None:
            book.file_format = payload.file_format
            logger.info(f"Updated file format to: {payload.file_format}")
            
        # Audio book fields
        if payload.duration_minutes is not None:
            book.duration_minutes = payload.duration_minutes
            logger.info(f"Updated duration to: {payload.duration_minutes}")
            
        if payload.narrator is not None:
            book.narrator = payload.narrator
            logger.info(f"Updated narrator to: {payload.narrator}")
        
        # Değişiklikleri kaydet
        library.save_books()
        
        logger.info(f"Successfully updated book: {book.title}")
        return BookResponse(**vars(book))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the book"
        )

@app.post("/books/{isbn}/borrow", response_model=BookResponse, tags=["Books"])
async def borrow_return_book(isbn: str, payload: BorrowRequest):
    """
    Kitap ödünç alma/iade işlemi
    
    Args:
        isbn (str): Kitabın ISBN'i
        payload (BorrowRequest): Action payload containing 'borrow' or 'return'
        
    Returns:
        BookResponse: Güncellenmiş kitap bilgileri
        
    Raises:
        HTTPException: Kitap bulunamadığında veya işlem yapılamadığında
    """
    try:
        action = payload.action
        logger.info(f"Book {action} request for ISBN: {isbn}")
        
        # Kitabı bul
        book = library.find_book(isbn)
        if not book:
            logger.warning(f"Book not found: {isbn}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ISBN {isbn} not found"
            )
        
        # İşlemi gerçekleştir
        if action == "borrow":
            if book.is_borrowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book '{book.title}' is already borrowed"
                )
            book.borrow_book()
            logger.info(f"Book borrowed: {book.title}")
            
        elif action == "return":
            if not book.is_borrowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book '{book.title}' was not borrowed"
                )
            book.return_book()
            logger.info(f"Book returned: {book.title}")
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Use 'borrow' or 'return'"
            )
        
        # Değişiklikleri kaydet
        library.save_books()
        
        return BookResponse(**vars(book))
        
    except HTTPException:
        raise
    except ValueError as e:
        # Book sınıfından gelen hatalar
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in borrow/return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during the operation"
        )

@app.get("/health", tags=["System"])
async def health_check():
    """
    API sağlık kontrolü
    
    Returns:
        dict: API durumu ve istatistikleri
    """
    try:
        book_count = len(list(library.list_books()))
        return {
            "status": "healthy",
            "api_version": "3.0.0",
            "total_books": book_count,
            "features": {
                "open_library_integration": True,
                "isbn_support": True,
                "json_persistence": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Library Management API...")
    uvicorn.run(
        "stage3_fastapi.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
