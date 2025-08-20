"""
Stage 3: FastAPI Web API
Kütüphane yönetim sistemi için REST API
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import logging

from stage3_fastapi.library import Library
from stage3_fastapi.models import ISBNRequest, BookResponse, ErrorResponse

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

# Global library instance
library = Library("library.json")  # library_api.json yerine

@app.get("/", tags=["Root"])
async def root():
    """API ana sayfa"""
    return {
        "message": "Library Management API - Stage 3",
        "version": "3.0.0",
        "features": ["Open Library Integration", "ISBN-based book addition", "Full CRUD operations"],
        "docs": "/docs",
        "redoc": "/redoc"
    }

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
        payload (ISBNRequest): ISBN içeren istek
        
    Returns:
        BookResponse: Eklenen kitap bilgileri
        
    Raises:
        HTTPException: Kitap eklenemediğinde (geçersiz ISBN, ağ hatası, vs.)
    """
    try:
        logger.info(f"Adding book with ISBN: {payload.isbn}")
        
        # ISBN ile kitap ekleme (Stage 2 fonksiyonalitesi)
        result = library.add_book(payload.isbn)
        
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
