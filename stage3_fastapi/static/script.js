// API Base URL
const API_BASE = '';

// Global state
let allBooks = [];

// DOM Elements
const loadingElement = document.getElementById('loading');
const booksGrid = document.getElementById('books-grid');
const addForm = document.getElementById('add-book-form');
const addResult = document.getElementById('add-result');
const searchForm = document.getElementById('search-form');
const searchResult = document.getElementById('search-result');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadBooks();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Add book form
    addForm.addEventListener('submit', handleAddBook);
    
    // Search form
    searchForm.addEventListener('submit', handleSearch);
    
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            showTab(tabName);
        });
    });
}

// Tab management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load books when books tab is shown
    if (tabName === 'books') {
        loadBooks();
    }
}

// Show/hide loading
function showLoading(show = true) {
    if (show) {
        loadingElement.classList.remove('hidden');
        booksGrid.classList.add('hidden');
    } else {
        loadingElement.classList.add('hidden');
        booksGrid.classList.remove('hidden');
    }
}

// Show toast message
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <strong>${type === 'error' ? 'Hata:' : type === 'success' ? 'Başarılı:' : 'Bilgi:'}</strong>
        ${message}
    `;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Load all books
async function loadBooks() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/books`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        allBooks = await response.json();
        displayBooks(allBooks);
        
    } catch (error) {
        console.error('Error loading books:', error);
        showToast(`Kitaplar yüklenirken hata: ${error.message}`, 'error');
        booksGrid.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Kitaplar yüklenirken bir hata oluştu.</p>
                <button onclick="loadBooks()" class="btn btn-primary">
                    <i class="fas fa-retry"></i> Tekrar Dene
                </button>
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

// Display books in grid
function displayBooks(books) {
    if (!books || books.length === 0) {
        booksGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-book-open"></i>
                <h3>Henüz kitap yok</h3>
                <p>İlk kitabınızı eklemek için "Kitap Ekle" sekmesini kullanın.</p>
                <button onclick="showTab('add')" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Kitap Ekle
                </button>
            </div>
        `;
        return;
    }
    
    booksGrid.innerHTML = books.map(book => createBookCard(book)).join('');
}

// Create book card HTML
function createBookCard(book) {
    const authors = Array.isArray(book.authors) ? book.authors.join(', ') : book.authors || 'Bilinmeyen Yazar';
    const borrowedStatus = book.is_borrowed ? 
        '<span class="status borrowed"><i class="fas fa-user"></i> Ödünç Verildi</span>' : 
        '<span class="status available"><i class="fas fa-check"></i> Mevcut</span>';
    
    return `
        <div class="book-card" data-isbn="${book.isbn}">
            <h3>${escapeHtml(book.title)}</h3>
            <div class="book-authors">
                <i class="fas fa-user"></i> ${escapeHtml(authors)}
            </div>
            <div class="book-isbn">
                <i class="fas fa-barcode"></i> ISBN: ${escapeHtml(book.isbn)}
            </div>
            ${borrowedStatus}
            <div class="book-actions">
                <button onclick="viewBookDetails('${book.isbn}')" class="btn btn-secondary">
                    <i class="fas fa-eye"></i> Detay
                </button>
                <button onclick="deleteBook('${book.isbn}')" class="btn btn-danger">
                    <i class="fas fa-trash"></i> Sil
                </button>
            </div>
        </div>
    `;
}

// Handle add book form submission
async function handleAddBook(event) {
    event.preventDefault();
    
    const isbnInput = document.getElementById('isbn-input');
    const isbn = isbnInput.value.trim();
    
    if (!isbn) {
        showToast('Lütfen geçerli bir ISBN girin.', 'error');
        return;
    }
    
    try {
        // Show loading state
        const submitButton = addForm.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ekleniyor...';
        submitButton.disabled = true;
        
        addResult.classList.add('hidden');
        
        const response = await fetch(`${API_BASE}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ isbn: isbn })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success
            addResult.className = 'result-message success';
            addResult.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <strong>Başarılı!</strong> "${data.title}" kitabı kütüphaneye eklendi.
            `;
            addResult.classList.remove('hidden');
            
            // Clear form
            isbnInput.value = '';
            
            // Show success toast
            showToast(`"${data.title}" kitabı başarıyla eklendi.`, 'success');
            
            // Refresh books list if on books tab
            if (document.getElementById('books-tab').classList.contains('active')) {
                loadBooks();
            }
            
        } else {
            // Error
            addResult.className = 'result-message error';
            addResult.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <strong>Hata!</strong> ${data.detail || 'Kitap eklenemedi.'}
            `;
            addResult.classList.remove('hidden');
            
            showToast(data.detail || 'Kitap eklenemedi.', 'error');
        }
        
    } catch (error) {
        console.error('Error adding book:', error);
        addResult.className = 'result-message error';
        addResult.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Ağ Hatası!</strong> ${error.message}
        `;
        addResult.classList.remove('hidden');
        
        showToast(`Ağ hatası: ${error.message}`, 'error');
        
    } finally {
        // Restore button
        const submitButton = addForm.querySelector('button[type="submit"]');
        submitButton.innerHTML = '<i class="fas fa-plus"></i> Kitap Ekle';
        submitButton.disabled = false;
    }
}

// Handle search form submission
async function handleSearch(event) {
    event.preventDefault();
    
    const searchInput = document.getElementById('search-isbn');
    const isbn = searchInput.value.trim();
    
    if (!isbn) {
        showToast('Lütfen bir ISBN girin.', 'error');
        return;
    }
    
    try {
        searchResult.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Aranıyor...</div>';
        searchResult.classList.remove('hidden');
        
        const response = await fetch(`${API_BASE}/books/${encodeURIComponent(isbn)}`);
        
        if (response.ok) {
            const book = await response.json();
            searchResult.innerHTML = `
                <div class="search-success">
                    <h3><i class="fas fa-check-circle"></i> Kitap Bulundu</h3>
                    ${createBookCard(book)}
                </div>
            `;
        } else if (response.status === 404) {
            searchResult.innerHTML = `
                <div class="result-message info">
                    <i class="fas fa-info-circle"></i>
                    <strong>Bulunamadı</strong> ISBN "${isbn}" ile kitap bulunamadı.
                </div>
            `;
        } else {
            const data = await response.json();
            searchResult.innerHTML = `
                <div class="result-message error">
                    <i class="fas fa-exclamation-circle"></i>
                    <strong>Hata!</strong> ${data.detail || 'Arama hatası.'}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error searching:', error);
        searchResult.innerHTML = `
            <div class="result-message error">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Ağ Hatası!</strong> ${error.message}
            </div>
        `;
        showToast(`Arama hatası: ${error.message}`, 'error');
    }
}

// View book details
function viewBookDetails(isbn) {
    const book = allBooks.find(b => b.isbn === isbn);
    if (!book) {
        showToast('Kitap bilgileri bulunamadı.', 'error');
        return;
    }
    
    const authors = Array.isArray(book.authors) ? book.authors.join(', ') : book.authors || 'Bilinmeyen Yazar';
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h2><i class="fas fa-book"></i> Kitap Detayları</h2>
                <button onclick="this.closest('.modal-overlay').remove()" class="btn-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="book-detail">
                    <h3>${escapeHtml(book.title)}</h3>
                    <p><strong>Yazar(lar):</strong> ${escapeHtml(authors)}</p>
                    <p><strong>ISBN:</strong> ${escapeHtml(book.isbn)}</p>
                    <p><strong>Durum:</strong> ${book.is_borrowed ? 'Ödünç Verildi' : 'Mevcut'}</p>
                </div>
            </div>
            <div class="modal-footer">
                <button onclick="this.closest('.modal-overlay').remove()" class="btn btn-secondary">
                    <i class="fas fa-times"></i> Kapat
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Delete book
async function deleteBook(isbn) {
    const book = allBooks.find(b => b.isbn === isbn);
    const bookTitle = book ? book.title : isbn;
    
    if (!confirm(`"${bookTitle}" kitabını silmek istediğinizden emin misiniz?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/books/${encodeURIComponent(isbn)}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast(`"${bookTitle}" kitabı başarıyla silindi.`, 'success');
            
            // Remove from local array
            allBooks = allBooks.filter(b => b.isbn !== isbn);
            displayBooks(allBooks);
            
        } else if (response.status === 404) {
            showToast('Kitap bulunamadı.', 'error');
        } else {
            const data = await response.json();
            showToast(data.detail || 'Kitap silinemedi.', 'error');
        }
        
    } catch (error) {
        console.error('Error deleting book:', error);
        showToast(`Silme hatası: ${error.message}`, 'error');
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Add modal styles dynamically
const modalStyles = `
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    }
    
    .modal {
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        max-width: 500px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        animation: slideUp 0.3s ease;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .modal-header h2 {
        margin: 0;
        color: #2c3e50;
        font-size: 1.5rem;
    }
    
    .btn-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        color: #6c757d;
        cursor: pointer;
        padding: 5px;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    .btn-close:hover {
        background: #f8f9fa;
        color: #495057;
    }
    
    .modal-body {
        padding: 20px;
    }
    
    .book-detail h3 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.3rem;
    }
    
    .book-detail p {
        margin-bottom: 10px;
        color: #555;
        line-height: 1.6;
    }
    
    .modal-footer {
        padding: 20px;
        border-top: 1px solid #e9ecef;
        text-align: right;
    }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #6c757d;
        grid-column: 1 / -1;
    }
    
    .empty-state i {
        font-size: 4rem;
        color: #dee2e6;
        margin-bottom: 20px;
    }
    
    .empty-state h3 {
        color: #495057;
        margin-bottom: 10px;
        font-size: 1.5rem;
    }
    
    .empty-state p {
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    
    .error-message {
        text-align: center;
        padding: 60px 20px;
        color: #dc3545;
        grid-column: 1 / -1;
    }
    
    .error-message i {
        font-size: 3rem;
        margin-bottom: 20px;
    }
    
    .error-message p {
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    
    .status {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 15px;
    }
    
    .status.available {
        background: #d4edda;
        color: #155724;
    }
    
    .status.borrowed {
        background: #fff3cd;
        color: #856404;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;

// Inject modal styles
const styleSheet = document.createElement('style');
styleSheet.textContent = modalStyles;
document.head.appendChild(styleSheet);