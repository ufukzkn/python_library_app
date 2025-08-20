# 📚 Library Management System - Kütüphane Yönetim Sistemi

Bu proje, **Global AI Hub Python 202 Bootcamp** kapsamında geliştirilmiş 3 aşamalı bir kütüphane yönetim sistemidir. Temel OOP yapısından başlayarak REST API'ye kadar ilerleyen modüler bir mimariye sahiptir.

## 🎯 Proje Açıklaması

Bu kütüphane yönetim sistemi şu özelliklere sahiptir:

- **Stage 1**: Temel OOP yapısı, JSON kalıcılık, birim testleri
- **Stage 2**: Open Library API entegrasyonu, ISBN ile otomatik kitap ekleme
- **Stage 3**: FastAPI REST API, Swagger dokümantasyonu, interaktif API arayüzü

**Teknolojiler**: Python 3.13, FastAPI, Pydantic, httpx, pytest, Open Library API

## 🚀 Kurulum

### 1. Repoyu Klonlayın

```bash
git clone https://github.com/ufukzkn/python_library_app.git
cd python_library_app
```

### 2. Virtual Environment Oluşturun (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Bağımlılıkları Kurun

```bash
pip install -r requirements.txt
```

**Not**: PowerShell execution policy hatası alırsanız:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 💻 Kullanım

### Stage 1 & 2: Terminal Uygulaması

**CLI menüsü ile interaktif kullanım:**

```bash
# Stage 1 (Temel kütüphane)
python stage1_oop/main.py

# Stage 2 (API entegrasyonu ile)
python stage2_api/main.py

# Stage 3 (En güncel CLI)
python stage3_fastapi/main.py
```

**CLI Özellikleri:**

- Manuel kitap ekleme (Stage 1 tarzı)
- ISBN ile otomatik kitap ekleme (Stage 2 tarzı - Open Library API)
- Kitap arama, listeleme ve silme
- JSON kalıcılık

### Stage 3: API Sunucusu

**FastAPI REST API başlatma:**

```bash
# API sunucusunu başlatın
cd stage3_fastapi
uvicorn api:app --reload
```

**API erişim adresleri:**

- **API Ana Sayfa**: <http://127.0.0.1:8000/>
- **Swagger UI (İnteraktif Dokümantasyon)**: <http://127.0.0.1:8000/docs>
- **ReDoc**: <http://127.0.0.1:8000/redoc>
- **Health Check**: <http://127.0.0.1:8000/health>

## 📖 API Dokümantasyonu

### Endpoint'ler

| Method | Endpoint | Açıklama | Body |
|--------|----------|----------|------|
| `GET` | `/` | API bilgisi ve sürüm | - |
| `GET` | `/health` | Sistem durumu kontrolü | - |
| `GET` | `/books` | Tüm kitapları listele | - |
| `POST` | `/books` | ISBN ile kitap ekle | `{"isbn": "9780140328721"}` |
| `GET` | `/books/{isbn}` | Belirli kitabı getir | - |
| `DELETE` | `/books/{isbn}` | Kitabı sil | - |

### Örnek API İstekleri

**1. Kitap Ekleme:**

```bash
curl -X POST "http://127.0.0.1:8000/books" \
     -H "Content-Type: application/json" \
     -d '{"isbn": "9780140328721"}'
```

**Response (201 Created):**

```json
{
  "isbn": "9780140328721",
  "title": "Fantastic Mr. Fox",
  "authors": ["Roald Dahl"],
  "is_borrowed": false
}
```

**2. Tüm Kitapları Listeleme:**

```bash
curl "http://127.0.0.1:8000/books"
```

**3. Belirli Kitap Getirme:**

```bash
curl "http://127.0.0.1:8000/books/9780140328721"
```

**4. Kitap Silme:**

```bash
curl -X DELETE "http://127.0.0.1:8000/books/9780140328721"
```

### Hata Kodları

- `400 Bad Request`: Geçersiz ISBN veya duplicate kitap
- `404 Not Found`: Kitap bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## 🧪 Test Senaryoları

### Test Çalıştırma

```bash
# Tüm testleri çalıştır (43 test)
pytest -v

# Stage bazında testler
pytest stage1_oop/tests/ -v     # 4 test
pytest stage2_api/tests/ -v     # 10 test  
pytest stage3_fastapi/tests/ -v # 29 test
```

### Test Kapsamı

**Stage 1 Testleri:**

- ✅ Book sınıfı: `__str__` formatı, ödünç alma/iade
- ✅ Library sınıfı: CRUD operasyonları, JSON kalıcılık
- ✅ Exception handling: Double borrow/return

**Stage 2 Testleri:**

- ✅ API entegrasyonu: Open Library'den kitap çekme
- ✅ Error handling: 404, network errors, malformed JSON
- ✅ Stage 1 compatibility: Mevcut özellikler korundu
- ✅ Mixed operations: Manuel + API ile ekleme

**Stage 3 Testleri:**

- ✅ FastAPI endpoints: Tüm CRUD operasyonları
- ✅ HTTP status codes: 200, 201, 204, 400, 404
- ✅ Request/Response validation: Pydantic modelleri
- ✅ Error scenarios: Invalid ISBN, duplicates, network errors
- ✅ API workflow: End-to-end senaryolar

### Demo Scriptleri

**Stage 2 Demo:**

```bash
python stage2_api/stage2_demo.py
```

- Stage 1 ve Stage 2 özelliklerini test eder
- `stage1_demo.json` ve `stage2_demo.json` dosyaları oluşturur

**Stage 3 Demo:**

```bash
# Önce API'yi başlatın, yani 

stage3_fastapi dizininde: uvicorn api:app --reload 

# sonra:
python stage3_fastapi/stage3_demo.py
```

- Tüm API endpoint'lerini test eder
- HTTP isteklerini simüle eder

## 📁 Proje Yapısı

```text
python_oop_kutuphane/
├── stage1_oop/                  # Stage 1: Temel OOP
│   ├── models.py               # Book veri sınıfı
│   ├── library.py              # Library yönetimi + JSON
│   ├── main.py                 # CLI arayüzü
│   └── tests/                  # Birim testleri
├── stage2_api/                 # Stage 2: API Entegrasyonu  
│   ├── models.py               # Geliştirilmiş Book modeli
│   ├── library.py              # Open Library API entegrasyonu
│   ├── main.py                 # Gelişmiş CLI
│   ├── stage2_demo.py          # Demo script
│   └── tests/                  # API testleri
├── stage3_fastapi/             # Stage 3: FastAPI Web API
│   ├── models.py               # Pydantic modelleri
│   ├── library.py              # Library sınıfı (Stage 2'den)
│   ├── api.py                  # FastAPI uygulaması ⭐
│   ├── main.py                 # CLI (Stage 2'den)
│   ├── stage3_demo.py          # API demo
│   ├── test_stage3.py          # FastAPI test runner
│   └── tests/                  # FastAPI testleri
├── requirements.txt            # Bağımlılıklar
├── pytest.ini                 # Test konfigürasyonu
└── README.md                   # Bu dosya
```

## 🔧 Teknik Detaylar

### Veri Modeli

```python
# Book sınıfı (Stage 1-2)
@dataclass
class Book:
    isbn: str
    title: str  
    authors: List[str]
    is_borrowed: bool = False

# Pydantic modeli (Stage 3)
class BookResponse(BaseModel):
    isbn: str
    title: str
    authors: List[str]
    is_borrowed: bool = False
```

### API Entegrasyonu

- **Open Library API**: <https://openlibrary.org/isbn/{isbn}.json>
- **HTTP Client**: httpx (async support)
- **Error Handling**: Network errors, 404, timeout, malformed JSON
- **Fallback Strategy**: API hataları durumunda graceful degradation

### Özellikler

- ✅ **Stage 1 Compatibility**: Tüm aşamalar geriye uyumlu
- ✅ **Unified Data Storage**: CLI ve API aynı JSON dosyasını kullanır
- ✅ **Comprehensive Testing**: 43 test ile %100 coverage
- ✅ **Modern Python**: Type hints, async/await, Pydantic
- ✅ **Production Ready**: Logging, error handling, validation

## 🎓 Öğrenilen Teknolojiler

- **OOP**: Sınıflar, inheritance, encapsulation
- **API Integration**: REST API'ler, HTTP clients, error handling  
- **Web Development**: FastAPI, async programming, OpenAPI
- **Testing**: pytest, fixtures, mocking, test-driven development
- **Data Validation**: Pydantic modelleri, type checking
- **Documentation**: Swagger/OpenAPI, kod dokümantasyonu

---

**Proje**: Global AI Hub Python 202 Bootcamp Final Project  
**Geliştirici**: [ufukzkn](https://github.com/ufukzkn)  
**Teknolojiler**: Python 3.13 • FastAPI • pytest • Open Library API
