// Library Management System JavaScript - Enhanced Version
const API_BASE = '';

// Global variables
let currentBooks = [];
let currentFilter = 'all';
let currentPage = 1;
let pageSize = 15;
let totalPages = 1;

// Toast notification function
function showToast(message, type = 'success') {
    const toastHtml = `
        <div class="toast align-items-center text-bg-${type}" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    const toastContainer = document.querySelector('.toast-container');
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove after hiding
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Check API status
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        document.getElementById('apiStatus').innerHTML = `
            <i class="fas fa-check-circle text-success me-2"></i>
            <span class="text-success">API Online</span>
            <small class="text-muted ms-2">(${data.total_books} books)</small>
        `;
    } catch (error) {
        document.getElementById('apiStatus').innerHTML = `
            <i class="fas fa-times-circle text-danger me-2"></i>
            <span class="text-danger">API Offline</span>
        `;
    }
}

// Fetch and display books
async function fetchBooks() {
    try {
        const response = await fetch(`${API_BASE}/books`);
        const books = await response.json();
        
        currentBooks = books;
        displayBooks(books, currentFilter);
        updateStatistics(books);
        
    } catch (error) {
        document.getElementById('booksList').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Failed to load books. Make sure the API server is running.
            </div>
        `;
    }
}

// Display books with pagination and filtering
function displayBooks(books, filter = 'all') {
    const booksList = document.getElementById('booksList');
    const bookCount = document.getElementById('bookCount');
    
    // Filter books
    let filteredBooks = books;
    switch(filter) {
        case 'available':
            filteredBooks = books.filter(book => !book.is_borrowed);
            break;
        case 'borrowed':
            filteredBooks = books.filter(book => book.is_borrowed);
            break;
        case 'physical':
            filteredBooks = books.filter(book => (book.book_type || 'Physical') === 'Physical');
            break;
        case 'digital':
            filteredBooks = books.filter(book => book.book_type === 'Digital');
            break;
        case 'audio':
            filteredBooks = books.filter(book => book.book_type === 'Audio');
            break;
        default:
            filteredBooks = books;
    }
    
    updatePagination(filteredBooks.length);
    const paginatedBooks = getPaginatedBooks(filteredBooks, currentPage, pageSize);
    
    bookCount.textContent = `${filteredBooks.length} books`;
    
    if (filteredBooks.length === 0) {
        booksList.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-book-open fa-3x mb-3"></i>
                <p>No books found matching the current filter.</p>
                <p>Try changing the filter or add your first book!</p>
            </div>
        `;
        return;
    }

    const booksHtml = paginatedBooks.map((book, index) => {
        const globalIndex = (currentPage - 1) * pageSize + index;
        const bookType = book.book_type || 'Physical';
        
        return `
        <div class="book-card" data-book-type="${bookType}" data-borrowed="${book.is_borrowed}">
            <div class="book-header" onclick="toggleBookCard(${globalIndex})">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">
                            ${getBookTypeIcon(bookType)} ${book.title}
                            ${book.is_borrowed ? '<span class="badge bg-warning ms-2">Borrowed</span>' : '<span class="badge bg-success ms-2">Available</span>'}
                        </h6>
                        <small class="text-muted">
                            <i class="fas fa-user"></i> ${book.authors.join(', ')} | 
                            <i class="fas fa-barcode"></i> ${book.isbn} |
                            <span class="badge bg-secondary">${bookType}</span>
                        </small>
                    </div>
                    <div>
                        <i class="fas fa-chevron-down" id="chevron-${globalIndex}"></i>
                    </div>
                </div>
            </div>
            <div class="book-content book-collapsed" id="content-${globalIndex}">
                <div class="row">
                    <div class="col-md-8">
                        <div class="mb-3">
                            <strong>Title:</strong> ${book.title}<br>
                            <strong>Authors:</strong> ${book.authors.join(', ')}<br>
                            <strong>ISBN:</strong> ${book.isbn}<br>
                            <strong>Type:</strong> <span class="badge bg-info">${bookType}</span>
                        </div>
                        
                        <!-- Type-specific information -->
                        ${getBookTypeSpecificInfo(book, bookType)}
                        
                        <div class="mb-3">
                            <strong>Status:</strong> 
                            ${book.is_borrowed 
                                ? '<span class="badge bg-warning">Currently Borrowed</span>' 
                                : '<span class="badge bg-success">Available for Borrowing</span>'
                            }
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="d-grid gap-2">
                            ${book.is_borrowed 
                                ? `<button class="btn btn-success" onclick="returnBook('${book.isbn}')">
                                    <i class="fas fa-undo"></i> Return Book
                                   </button>`
                                : `<button class="btn btn-warning" onclick="borrowBook('${book.isbn}')">
                                    <i class="fas fa-hand-holding"></i> Borrow Book
                                   </button>`
                            }
                            <button class="btn btn-outline-primary" onclick="editBook('${book.isbn}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-danger" onclick="deleteBook('${book.isbn}')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
    
    booksList.innerHTML = booksHtml;
}

// Helper functions
function getBookTypeIcon(type) {
    switch(type) {
        case 'Physical': return '📖';
        case 'Digital': return '💻';
        case 'Audio': return '🎧';
        default: return '📚';
    }
}

// Toggle individual book card
function toggleBookCard(index) {
    const content = document.getElementById(`content-${index}`);
    const chevron = document.getElementById(`chevron-${index}`);
    
    if (content.classList.contains('book-collapsed')) {
        content.classList.remove('book-collapsed');
        chevron.classList.remove('fa-chevron-down');
        chevron.classList.add('fa-chevron-up');
    } else {
        content.classList.add('book-collapsed');
        chevron.classList.remove('fa-chevron-up');
        chevron.classList.add('fa-chevron-down');
    }
}

// Toggle all books
function toggleAllBooks() {
    const allContents = document.querySelectorAll('.book-content');
    const toggleIcon = document.getElementById('toggleIcon');
    const toggleText = document.getElementById('toggleText');
    
    const isAnyOpen = Array.from(allContents).some(content => !content.classList.contains('book-collapsed'));
    
    if (isAnyOpen) {
        // Collapse all
        allContents.forEach((content, index) => {
            content.classList.add('book-collapsed');
            const chevron = document.getElementById(`chevron-${index}`);
            if (chevron) {
                chevron.classList.remove('fa-chevron-up');
                chevron.classList.add('fa-chevron-down');
            }
        });
        toggleIcon.className = 'fas fa-eye';
        toggleText.textContent = 'Show All';
    } else {
        // Expand all
        allContents.forEach((content, index) => {
            content.classList.remove('book-collapsed');
            const chevron = document.getElementById(`chevron-${index}`);
            if (chevron) {
                chevron.classList.remove('fa-chevron-down');
                chevron.classList.add('fa-chevron-up');
            }
        });
        toggleIcon.className = 'fas fa-eye-slash';
        toggleText.textContent = 'Hide All';
    }
}

// Toggle books section
function toggleBooksSection() {
    const section = document.getElementById('booksSection');
    const chevron = document.getElementById('booksChevron');
    
    if (section.classList.contains('book-collapsed')) {
        section.classList.remove('book-collapsed');
        chevron.classList.remove('fa-chevron-down');
        chevron.classList.add('fa-chevron-up');
        
        if (currentBooks.length === 0) {
            fetchBooks();
        }
    } else {
        section.classList.add('book-collapsed');
        chevron.classList.remove('fa-chevron-up');
        chevron.classList.add('fa-chevron-down');
    }
}

// Pagination functions
function getPaginatedBooks(books, page, size) {
    const startIndex = (page - 1) * size;
    const endIndex = startIndex + size;
    return books.slice(startIndex, endIndex);
}

function updatePagination(totalBooks) {
    totalPages = Math.ceil(totalBooks / pageSize);
    
    const pageInfo = document.getElementById('pageInfo');
    const paginationNav = document.getElementById('paginationNav');
    
    if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages} (${totalBooks} total books)`;
    
    if (paginationNav) {
        if (totalPages > 1) {
            paginationNav.style.display = 'block';
            
            // Create advanced pagination
            let paginationHtml = `
                <ul class="pagination justify-content-center align-items-center">
                    <li class="page-item ${currentPage <= 1 ? 'disabled' : ''}" id="prevPage">
                        <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">
                            <i class="fas fa-chevron-left"></i> Previous
                        </a>
                    </li>
            `;
            
            // Show page numbers with ellipsis for large page counts
            const maxVisiblePages = 5;
            let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            // Adjust start if we're near the end
            if (endPage - startPage < maxVisiblePages - 1) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            // First page and ellipsis
            if (startPage > 1) {
                paginationHtml += `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="changePage(1)">1</a>
                    </li>
                `;
                if (startPage > 2) {
                    paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
                }
            }
            
            // Page numbers
            for (let i = startPage; i <= endPage; i++) {
                paginationHtml += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                    </li>
                `;
            }
            
            // Last page and ellipsis
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
                }
                paginationHtml += `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="changePage(${totalPages})">${totalPages}</a>
                    </li>
                `;
            }
            
            paginationHtml += `
                    <li class="page-item ${currentPage >= totalPages ? 'disabled' : ''}" id="nextPage">
                        <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">
                            Next <i class="fas fa-chevron-right"></i>
                        </a>
                    </li>
                    <li class="page-item">
                        <div class="page-link p-1">
                            <div class="input-group input-group-sm" style="width: 120px;">
                                <input type="number" class="form-control form-control-sm" 
                                       placeholder="Page" min="1" max="${totalPages}" 
                                       id="pageInput" onkeypress="handlePageInputEnter(event)">
                                <button class="btn btn-outline-secondary btn-sm" type="button" onclick="goToPage()">
                                    <i class="fas fa-arrow-right"></i>
                                </button>
                            </div>
                        </div>
                    </li>
                </ul>
            `;
            
            paginationNav.innerHTML = paginationHtml;
        } else {
            paginationNav.style.display = 'none';
        }
    }
}

function changePage(newPage) {
    if (newPage < 1 || newPage > totalPages) return;
    
    // Remember scroll position
    const scrollPosition = window.pageYOffset;
    
    currentPage = newPage;
    displayBooks(currentBooks, currentFilter);
    
    // Restore scroll position after a brief delay to let DOM update
    setTimeout(() => {
        window.scrollTo(0, scrollPosition);
    }, 50);
}

function changePageSize() {
    const pageSizeElement = document.getElementById('pageSize');
    if (pageSizeElement) {
        const newSize = parseInt(pageSizeElement.value);
        pageSize = newSize;
        currentPage = 1;
        displayBooks(currentBooks, currentFilter);
    }
}

function goToPage() {
    const pageInput = document.getElementById('pageInput');
    if (pageInput) {
        const pageNumber = parseInt(pageInput.value);
        if (pageNumber && pageNumber >= 1 && pageNumber <= totalPages) {
            changePage(pageNumber);
            pageInput.value = '';
        } else {
            showToast('❌ Invalid page number', 'danger');
        }
    }
}

function handlePageInputEnter(event) {
    if (event.key === 'Enter') {
        goToPage();
    }
}

function filterBooks(filter) {
    currentFilter = filter;
    currentPage = 1;
    
    // Update button states
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const filterBtn = document.getElementById(`filter-${filter}`);
    if (filterBtn) filterBtn.classList.add('active');
    
    displayBooks(currentBooks, filter);
}

// Update statistics
function updateStatistics(books) {
    const totalBooks = books.length;
    const borrowedBooks = books.filter(book => book.is_borrowed).length;
    const physicalBooks = books.filter(book => (book.book_type || 'Physical') === 'Physical').length;
    const digitalBooks = books.filter(book => book.book_type === 'Digital').length;
    const audioBooks = books.filter(book => book.book_type === 'Audio').length;
    
    const totalBooksEl = document.getElementById('totalBooks');
    const borrowedBooksEl = document.getElementById('borrowedBooks');
    const physicalBooksEl = document.getElementById('physicalBooks');
    const digitalBooksEl = document.getElementById('digitalBooks');
    const audioBooksEl = document.getElementById('audioBooks');
    
    if (totalBooksEl) totalBooksEl.textContent = totalBooks;
    if (borrowedBooksEl) borrowedBooksEl.textContent = borrowedBooks;
    if (physicalBooksEl) physicalBooksEl.textContent = physicalBooks;
    if (digitalBooksEl) digitalBooksEl.textContent = digitalBooks;
    if (audioBooksEl) audioBooksEl.textContent = audioBooks;
}

// Add book by ISBN
async function addBook(isbn, bookType = 'Physical', extraData = {}) {
    try {
        const payload = { 
            isbn,
            book_type: bookType,
            ...extraData
        };
        
        console.log('Sending book data:', payload);
        
        const response = await fetch(`${API_BASE}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const book = await response.json();
            showToast(`✅ Book added: ${book.title}`, 'success');
            fetchBooks();
            checkApiStatus();
        } else {
            const error = await response.json();
            showToast(`❌ Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showToast('❌ Network error. Check if API is running.', 'danger');
    }
}

// Add manual book
async function addManualBook(bookData) {
    try {
        console.log('Sending manual book data:', bookData);
        
        const response = await fetch(`${API_BASE}/books/manual`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookData)
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
            const book = await response.json();
            showToast(`✅ Manual book added: ${book.title}`, 'success');
            fetchBooks();
            checkApiStatus();
        } else {
            const errorText = await response.text();
            console.error('Manual book error:', response.status, errorText);
            
            let errorDetail = 'Unknown error';
            try {
                const errorJson = JSON.parse(errorText);
                errorDetail = errorJson.detail || errorText;
            } catch {
                errorDetail = errorText;
            }
            
            showToast(`❌ Manual book error (${response.status}): ${errorDetail}`, 'danger');
        }
    } catch (error) {
        console.error('Network error:', error);
        showToast(`❌ Network error: ${error.message}`, 'danger');
    }
}

// Borrow book
async function borrowBook(isbn) {
    try {
        // Find the book to determine current status
        const book = currentBooks.find(b => b.isbn === isbn);
        if (!book) {
            showToast('❌ Book not found', 'danger');
            return;
        }
        
        // Determine action based on current status
        const action = book.is_borrowed ? 'return' : 'borrow';
        
        const response = await fetch(`${API_BASE}/books/${isbn}/borrow`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action })
        });

        if (response.ok) {
            const updatedBook = await response.json();
            const actionText = action === 'borrow' ? 'borrowed' : 'returned';
            const icon = action === 'borrow' ? '📚' : '📖';
            showToast(`${icon} Book ${actionText}: ${updatedBook.title}`, 'success');
            
            // Refresh books and update search results if any
            fetchBooks();
            
            // If there are search results, refresh them too
            const searchQuery = document.getElementById('searchQuery')?.value?.trim();
            if (searchQuery) {
                // Small delay to ensure currentBooks is updated
                setTimeout(() => {
                    searchBooks(searchQuery);
                }, 100);
            }
            
            checkApiStatus();
        } else {
            const error = await response.json();
            showToast(`❌ Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showToast('❌ Network error. Check if API is running.', 'danger');
    }
}

// Edit book function - MODERN VERSION WITH MODAL
function editBook(isbn) {
    // Find the book
    const book = currentBooks.find(b => b.isbn === isbn);
    if (!book) {
        showToast('❌ Book not found', 'danger');
        return;
    }
    
    // Populate edit form with current values
    document.getElementById('editBookIsbn').value = book.isbn;
    document.getElementById('editTitle').value = book.title;
    document.getElementById('editAuthors').value = book.authors.join(', ');
    document.getElementById('editBookType').value = book.book_type || 'Physical';
    document.getElementById('editBorrowStatus').value = book.is_borrowed.toString();
    document.getElementById('editIsbn').value = book.isbn;
    
    // Update dynamic fields based on book type FIRST
    updateEditBookTypeFields();
    
    // THEN populate type-specific fields if they exist (after a small delay to ensure fields are created)
    setTimeout(() => {
        if (book.book_type === 'Physical' && book.shelf_location) {
            const shelfField = document.getElementById('editShelfLocation');
            if (shelfField) shelfField.value = book.shelf_location;
        } else if (book.book_type === 'Digital') {
            const fileSizeField = document.getElementById('editFileSize');
            const fileFormatField = document.getElementById('editFileFormat');
            if (fileSizeField && book.file_size_mb) fileSizeField.value = book.file_size_mb;
            if (fileFormatField && book.file_format) fileFormatField.value = book.file_format;
        } else if (book.book_type === 'Audio') {
            const durationField = document.getElementById('editDuration');
            const narratorField = document.getElementById('editNarrator');
            if (durationField && book.duration_minutes) durationField.value = book.duration_minutes;
            if (narratorField && book.narrator) narratorField.value = book.narrator;
        }
    }, 10);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('editBookModal'));
    modal.show();
}

// Update edit form dynamic fields based on book type
function updateEditBookTypeFields() {
    const bookType = document.getElementById('editBookType').value;
    const extraFields = document.getElementById('editExtraFields');
    
    if (bookType === 'Physical') {
        extraFields.innerHTML = `
            <div class="mb-3">
                <label for="editShelfLocation" class="form-label">Shelf Location</label>
                <input type="text" class="form-control" id="editShelfLocation" placeholder="A1-001">
            </div>
        `;
    } else if (bookType === 'Digital') {
        extraFields.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="editFileSize" class="form-label">File Size (MB)</label>
                        <input type="number" class="form-control" id="editFileSize" placeholder="5.0" step="0.1">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="editFileFormat" class="form-label">Format</label>
                        <select class="form-control" id="editFileFormat">
                            <option value="">Select format</option>
                            <option value="PDF">PDF</option>
                            <option value="EPUB">EPUB</option>
                            <option value="MOBI">MOBI</option>
                            <option value="TXT">TXT</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    } else if (bookType === 'Audio') {
        extraFields.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="editDuration" class="form-label">Duration (minutes)</label>
                        <input type="number" class="form-control" id="editDuration" placeholder="480">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="editNarrator" class="form-label">Narrator</label>
                        <input type="text" class="form-control" id="editNarrator" placeholder="Narrator name">
                    </div>
                </div>
            </div>
        `;
    } else {
        extraFields.innerHTML = '';
    }
}

// Save book edit changes
async function saveBookEdit() {
    try {
        const isbn = document.getElementById('editBookIsbn').value;
        const title = document.getElementById('editTitle').value.trim();
        const authorsText = document.getElementById('editAuthors').value.trim();
        const bookType = document.getElementById('editBookType').value;
        const borrowStatus = document.getElementById('editBorrowStatus').value === 'true';
        
        // Validate required fields
        if (!title || !authorsText) {
            showToast('❌ Title and authors are required', 'danger');
            return;
        }
        
        // Parse authors
        const authors = authorsText.split(',').map(a => a.trim()).filter(a => a);
        if (authors.length === 0) {
            showToast('❌ At least one author is required', 'danger');
            return;
        }
        
        // Prepare update data
        const updateData = {
            title: title,
            authors: authors,
            is_borrowed: borrowStatus,
            book_type: bookType
        };
        
        // Add type-specific fields
        if (bookType === 'Physical') {
            const shelfLocation = document.getElementById('editShelfLocation')?.value;
            if (shelfLocation) updateData.shelf_location = shelfLocation;
        } else if (bookType === 'Digital') {
            const fileSize = document.getElementById('editFileSize')?.value;
            const fileFormat = document.getElementById('editFileFormat')?.value;
            if (fileSize) updateData.file_size_mb = parseFloat(fileSize);
            if (fileFormat) updateData.file_format = fileFormat;
        } else if (bookType === 'Audio') {
            const duration = document.getElementById('editDuration')?.value;
            const narrator = document.getElementById('editNarrator')?.value;
            if (duration) updateData.duration_minutes = parseInt(duration);
            if (narrator) updateData.narrator = narrator;
        }
        
        console.log('Updating book with data:', updateData);
        
        const response = await fetch(`${API_BASE}/books/${isbn}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            const updatedBook = await response.json();
            showToast(`✅ Book updated: ${updatedBook.title}`, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editBookModal'));
            modal.hide();
            
            // Refresh books list
            fetchBooks();
        } else {
            const errorText = await response.text();
            console.error('Update error:', response.status, errorText);
            
            let errorDetail = 'Unknown error';
            try {
                const errorJson = JSON.parse(errorText);
                errorDetail = errorJson.detail || errorText;
            } catch {
                errorDetail = errorText;
            }
            
            showToast(`❌ Update failed (${response.status}): ${errorDetail}`, 'danger');
        }
    } catch (error) {
        console.error('Edit book error:', error);
        showToast(`❌ Network error: ${error.message}`, 'danger');
    }
}

// Delete book
async function deleteBook(isbn) {
    if (!confirm('Are you sure you want to delete this book?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/books/${isbn}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('✅ Book deleted successfully', 'success');
            fetchBooks();
            checkApiStatus();
        } else {
            const error = await response.json();
            showToast(`❌ Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showToast('❌ Network error. Check if API is running.', 'danger');
    }
}

// Search books (local search)
function searchBooks(query) {
    try {
        if (!currentBooks || currentBooks.length === 0) {
            const searchResults = document.getElementById('searchResults');
            if (searchResults) {
                searchResults.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        No books loaded. Please load books first.
                    </div>
                `;
            }
            return;
        }
        
        const searchQuery = query.toLowerCase().trim();
        const matchedBooks = currentBooks.filter(book => 
            book.title.toLowerCase().includes(searchQuery) ||
            book.authors.some(author => author.toLowerCase().includes(searchQuery)) ||
            book.isbn.includes(searchQuery)
        );
        
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            if (matchedBooks.length === 0) {
                searchResults.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-search"></i>
                        No books found matching "${query}"
                    </div>
                `;
            } else {
                const resultsHtml = matchedBooks.map(book => {
                    const typeSpecificInfo = getBookTypeSpecificInfo(book, book.book_type || 'Physical');
                    return `
                        <div class="col-md-6 col-lg-4 mb-3">
                            <div class="card h-100 book-card">
                                <div class="card-body">
                                    <h6 class="card-title text-truncate">${book.title}</h6>
                                    <p class="card-text">
                                        <small class="text-muted">by ${book.authors.join(', ')}</small><br>
                                        <small>ISBN: ${book.isbn}</small><br>
                                        <span class="badge ${book.book_type === 'Physical' ? 'bg-primary' : 
                                                                book.book_type === 'Digital' ? 'bg-info' : 
                                                                book.book_type === 'Audio' ? 'bg-warning' : 'bg-secondary'}">
                                            ${book.book_type === 'Physical' ? '📚' : 
                                              book.book_type === 'Digital' ? '💻' : 
                                              book.book_type === 'Audio' ? '🎧' : '📖'} ${book.book_type || 'Physical'}
                                        </span>
                                        ${typeSpecificInfo}
                                    </p>
                                    <div class="d-flex gap-1">
                                        <button class="btn btn-sm ${book.is_borrowed ? 'btn-warning' : 'btn-success'}" 
                                                onclick="borrowBook('${book.isbn}')">
                                            <i class="fas ${book.is_borrowed ? 'fa-undo' : 'fa-hand-holding'}"></i>
                                            ${book.is_borrowed ? 'Return' : 'Borrow'}
                                        </button>
                                        <button class="btn btn-sm btn-outline-primary" onclick="editBook('${book.isbn}')">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" onclick="deleteBook('${book.isbn}')">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                searchResults.innerHTML = `
                    <div class="alert alert-success mb-3">
                        <i class="fas fa-check"></i> Found ${matchedBooks.length} book(s) matching "${query}"
                    </div>
                    <div class="row">
                        ${resultsHtml}
                    </div>
                `;
            }
        }
        
    } catch (error) {
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            searchResults.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Search failed: ${error.message}
                </div>
            `;
        }
    }
}

// Refresh books
function refreshBooks() {
    fetchBooks();
    checkApiStatus();
    showToast('🔄 Refreshed!', 'info');
}

// Dynamic form fields for book types
function updateBookTypeFields(selectElement, fieldsContainerId) {
    const bookType = selectElement.value;
    const extraFields = document.getElementById(fieldsContainerId);
    
    if (!extraFields) return;
    
    const isManual = fieldsContainerId === 'manualExtraFields';
    const prefix = isManual ? 'manual' : '';
    
    if (bookType === 'Physical') {
        extraFields.innerHTML = `
            <div class="mb-3">
                <label class="form-label">Shelf Location (optional)</label>
                <input type="text" class="form-control" id="${prefix}ShelfLocation" placeholder="A1-001">
            </div>
        `;
    } else if (bookType === 'Digital') {
        extraFields.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">File Size (MB)</label>
                        <input type="number" class="form-control" id="${prefix}FileSize" placeholder="5.0" step="0.1">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Format</label>
                        <select class="form-control" id="${prefix}FileFormat">
                            <option value="">Select format</option>
                            <option value="PDF">PDF</option>
                            <option value="EPUB">EPUB</option>
                            <option value="MOBI">MOBI</option>
                            <option value="TXT">TXT</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    } else if (bookType === 'Audio') {
        extraFields.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Duration (minutes)</label>
                        <input type="number" class="form-control" id="${prefix}Duration" placeholder="480">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Narrator</label>
                        <input type="text" class="form-control" id="${prefix}Narrator" placeholder="Narrator name">
                    </div>
                </div>
            </div>
        `;
    } else {
        extraFields.innerHTML = '';
    }
}

// Event listeners setup
function setupEventListeners() {
    // Book type change listeners
    const bookTypeSelect = document.getElementById('bookType');
    if (bookTypeSelect) {
        bookTypeSelect.addEventListener('change', function() {
            updateBookTypeFields(this, 'extraFields');
        });
    }
    
    const manualTypeSelect = document.getElementById('manualType');
    if (manualTypeSelect) {
        manualTypeSelect.addEventListener('change', function() {
            updateBookTypeFields(this, 'manualExtraFields');
        });
    }
    
    // ISBN form submit
    const addBookForm = document.getElementById('addBookForm');
    if (addBookForm) {
        addBookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const isbn = document.getElementById('isbn').value.trim();
            const bookType = document.getElementById('bookType').value || 'Physical';
            
            if (isbn) {
                // Collect extra fields based on book type
                const extraData = {};
                
                if (bookType === 'Physical') {
                    const shelfLocation = document.getElementById('ShelfLocation')?.value;
                    if (shelfLocation) extraData.shelf_location = shelfLocation;
                } else if (bookType === 'Digital') {
                    const fileSize = document.getElementById('FileSize')?.value;
                    const fileFormat = document.getElementById('FileFormat')?.value;
                    if (fileSize) extraData.file_size_mb = parseFloat(fileSize);
                    if (fileFormat) extraData.file_format = fileFormat;
                } else if (bookType === 'Audio') {
                    const duration = document.getElementById('Duration')?.value;
                    const narrator = document.getElementById('Narrator')?.value;
                    if (duration) extraData.duration_minutes = parseInt(duration);
                    if (narrator) extraData.narrator = narrator;
                }
                
                addBook(isbn, bookType, extraData);
                document.getElementById('isbn').value = '';
                const extraFields = document.getElementById('extraFields');
                if (extraFields) extraFields.innerHTML = '';
            }
        });
    }
    
    // Manual form submit
    const manualBookForm = document.getElementById('manualBookForm');
    if (manualBookForm) {
        manualBookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const title = document.getElementById('manualTitle').value.trim();
            const authorsInput = document.getElementById('manualAuthors').value.trim();
            const isbn = document.getElementById('manualIsbn').value.trim();
            const bookType = document.getElementById('manualType').value || 'Physical';
            
            // Authors validation - make sure we have at least one non-empty author
            const authors = authorsInput.split(',')
                .map(a => a.trim())
                .filter(a => a.length > 0);
            
            if (authors.length === 0) {
                showToast('❌ Please enter at least one author', 'danger');
                return;
            }
            
            const bookData = {
                title: title,
                authors: authors,
                isbn: isbn,
                book_type: bookType
            };
            
            // Add extra fields based on book type
            if (bookType === 'Physical') {
                const shelfLocation = document.getElementById('manualShelfLocation')?.value;
                if (shelfLocation) bookData.shelf_location = shelfLocation;
            } else if (bookType === 'Digital') {
                const fileSize = document.getElementById('manualFileSize')?.value;
                const fileFormat = document.getElementById('manualFileFormat')?.value;
                if (fileSize) bookData.file_size_mb = parseFloat(fileSize);
                if (fileFormat) bookData.file_format = fileFormat;
            } else if (bookType === 'Audio') {
                const duration = document.getElementById('manualDuration')?.value;
                const narrator = document.getElementById('manualNarrator')?.value;
                if (duration) bookData.duration_minutes = parseInt(duration);
                if (narrator) bookData.narrator = narrator;
            }
            
            console.log('Manual book data:', bookData); // Debug log
            
            if (title && authors.length > 0 && isbn) {
                addManualBook(bookData);
                manualBookForm.reset();
                const extraFields = document.getElementById('manualExtraFields');
                if (extraFields) extraFields.innerHTML = '';
            }
        });
    }
    
    // Search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('searchQuery').value.trim();
            if (query) {
                searchBooks(query);
            }
        });
    }
    
    // Edit modal book type change listener
    const editBookTypeSelect = document.getElementById('editBookType');
    if (editBookTypeSelect) {
        editBookTypeSelect.addEventListener('change', updateEditBookTypeFields);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Library Management System - Starting...');
    
    // Setup event listeners
    setupEventListeners();
    
    // Check API and load initial data
    checkApiStatus();
    fetchBooks();
    
    // Make sure books section is open by default
    const booksSection = document.getElementById('booksSection');
    const booksChevron = document.getElementById('booksChevron');
    if (booksSection && booksChevron) {
        booksSection.classList.remove('book-collapsed');
        booksChevron.classList.remove('fa-chevron-down');
        booksChevron.classList.add('fa-chevron-up');
    }
    
    console.log('Library Management System - Ready!');
});

// Helper function to generate type-specific information for book cards
function getBookTypeSpecificInfo(book, bookType) {
    let specificInfo = '';
    
    if (bookType === 'Physical') {
        if (book.shelf_location) {
            specificInfo = `
                <div class="mb-3">
                    <strong><i class="fas fa-map-marker-alt"></i> Shelf Location:</strong> 
                    <span class="badge bg-secondary">${book.shelf_location}</span>
                </div>
            `;
        }
    } else if (bookType === 'Digital') {
        let digitalInfo = [];
        if (book.file_size_mb) {
            digitalInfo.push(`<strong>📁 Size:</strong> ${book.file_size_mb} MB`);
        }
        if (book.file_format) {
            digitalInfo.push(`<strong>📄 Format:</strong> <span class="badge bg-primary">${book.file_format}</span>`);
        }
        if (digitalInfo.length > 0) {
            specificInfo = `
                <div class="mb-3">
                    ${digitalInfo.join('<br>')}
                </div>
            `;
        }
    } else if (bookType === 'Audio') {
        let audioInfo = [];
        if (book.duration_minutes) {
            const hours = Math.floor(book.duration_minutes / 60);
            const minutes = book.duration_minutes % 60;
            const duration = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
            audioInfo.push(`<strong>⏱️ Duration:</strong> ${duration}`);
        }
        if (book.narrator) {
            audioInfo.push(`<strong>🎙️ Narrator:</strong> ${book.narrator}`);
        }
        if (audioInfo.length > 0) {
            specificInfo = `
                <div class="mb-3">
                    ${audioInfo.join('<br>')}
                </div>
            `;
        }
    }
    
    return specificInfo;
}
