# 📚 Library Management System - Kütüphane Yönetim Sistemi

Bu proje, **Global AI Hub Python 202 Bootcamp** kapsamında geliştirilmiş 3 aşamalı bir kütüphane yönetim sistemidir. Temel OOP yapısından başlayarak REST API'ye kadar ilerleyen modüler bir mimariye sahiptir.

## 🎯 Proje Açıklaması

Bu kütüphane yönetim sistemi şu özelliklere sahiptir:

- **Stage 1**: Temel OOP yapısı, JSON kalıcılık, birim testleri
- **Stage 2**: Open Library API entegrasyonu, ISBN ile otomatik kitap ekleme
- **Stage 3**: FastAPI REST API, Swagger dokümantasyonu, interaktif API arayüzü

Her stage kendi başına bir Python **package** olarak yapılandırılmıştır.

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
uv pip install -r requirements.txt
```

**Not**: PowerShell execution policy hatası alırsanız:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 💻 Kullanım

**ÖNEMLİ NOT:**  
> Bu projede tüm stage'ler birer Python package olarak yapılandırılmıştır.  
> **Kök dizinde** main.py'leri çalıştırmak için -m eki aşağıdaki gibi kullanılmalıdır.

### Stage 1 & 2: Terminal Uygulaması

**CLI menüsü ile interaktif kullanım:**

```bash
# Stage 1 (Temel kütüphane)
python -m stage1_oop.main

# Stage 2 (API entegrasyonu ile)
python -m stage2_api.main

# Stage 3 (En güncel CLI)
python -m stage3_fastapi.main
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
uvicorn stage3_fastapi.api:app --reload 
```

**API erişim adresleri:**

- **API Ana Sayfa**: <http://127.0.0.1:8000/>
- **Web Arayüzü**: <http://127.0.0.1:8000/static/index.html>
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
| `PUT` | `/books/{isbn}` | Kitap bilgilerini güncelle | `{"title": "Yeni Başlık", "authors": ["Yazar"], "is_borrowed": false}` |
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

**4. Kitap Güncelleme:**

```bash
curl -X PUT "http://127.0.0.1:8000/books/9780140328721" \
     -H "Content-Type: application/json" \
     -d '{"title": "Fantastic Mr. Fox - Updated", "is_borrowed": true}'
```

**5. Kitap Silme:**

```bash
curl -X DELETE "http://127.0.0.1:8000/books/9780140328721"
```

### Hata Kodları

- `400 Bad Request`: Geçersiz ISBN veya duplicate kitap
- `404 Not Found`: Kitap bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## 🧪 Test Senaryoları

## 🔄 Aşamaların Kısa Özeti ve Örnek Çıktılar

### Stage 1: Konsol Tabanlı OOP Uygulaması

Kitap ekleme, silme, arama ve listeleme. JSON dosyasında veri saklama.

**Örnek Çıktı:**

```shell
[1] Add
[2] Remove
[3] List
[4] Find by ISBN
[0] Exit
Choose: 1
Title: Sapiens
Author: Yuval Noah Harari
ISBN: 9780062316097
Added.

[1] Add
[2] Remove
[3] List
[4] Find by ISBN
[0] Exit
Choose: 3
 1. Sapiens by Yuval Noah Harari (ISBN: 9780062316097)
```

### Stage 2: Open Library API ile ISBN’den Kitap Ekleme

Manuel ve otomatik ekleme birlikte kullanılabiliyor.

**Örnek Çıktı:**

```shell
[1] Add book manually (Stage 1 style)
[2] Add book by ISBN from API (Stage 2 style)
[3] Remove
[4] List
[5] Find by ISBN
[0] Exit
Choose: 2
ISBN: 9780140449136
Book successfully added: The Odyssey by Homer (ISBN: 9780140449136)

Choose: 4
 1. The Odyssey by Homer (ISBN: 9780140449136)
```

### Stage 3: FastAPI ile REST API

Swagger/OpenAPI arayüzü, HTTP endpoint’leri, otomatik testler ve demo scriptleri.

**Örnek API Çıktısı:**

```http
GET /health
200 OK
{
  "status": "ok"
}

GET /books
200 OK
[
  {
    "isbn": "9780140449136",
    "title": "The Odyssey",
    "authors": ["Homer"]
  }
]
```

**Örnek Test Çıktısı:**

```shell
=== Stage 3 FastAPI Files Check ===
✓ api.py found
✓ models.py found
✓ library.py found

=== Import Test ===
✓ Models imported successfully
✓ Library imported successfully
✓ FastAPI imported successfully
✓ API app imported successfully
✓ App type: <class 'fastapi.applications.FastAPI'>
✓ App title: Library API

=== FastAPI Manual Test ===
✓ Root endpoint response: 200
✓ Response data: {'message': 'Welcome to the Library API!'}
✓ Health endpoint response: 200
✓ Health data: {'status': 'ok'}
```

### Test Çalıştırma

```bash
# Tüm testleri çalıştır (43 test)
pytest -v

# Stage bazında testler
pytest stage1_oop/tests/ -v     # 4 test
pytest stage2_api/tests/ -v     # 10 test  
pytest stage3_fastapi/tests/ -v # 29 test
```

### Stage 3 FastAPI Dosya ve Import Testi

Stage 3 FastAPI package'ının dosya yapısı ve importlarının doğru olup olmadığını test etmek için aşağıdaki komutu kullanabilirsiniz:

```powershell
python -m stage3_fastapi.test_stage3
```

**Tipik Çıktı:**

```shell
=== Stage 3 FastAPI Files Check ===
✓ api.py found
✓ models.py found
✓ library.py found

=== Import Test ===
✓ Models imported successfully
✓ Library imported successfully
✓ FastAPI imported successfully
✓ API app imported successfully
✓ App type: <class 'fastapi.applications.FastAPI'>
✓ App title: Library API

=== FastAPI Manual Test ===
✓ Root endpoint response: 200
✓ Response data: {'message': 'Welcome to the Library API!'}
✓ Health endpoint response: 200
✓ Health data: {'status': 'ok'}
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
python -m stage2_api.stage2_demo
```

- Stage 1 ve Stage 2 özelliklerini test eder
- `stage1_demo.json` ve `stage2_demo.json` dosyaları oluşturur

**Stage 3 Demo:**

```bash
# Önce API'yi başlatın, yani 

uvicorn stage3_fastapi.api:app --reload 

# sonra:
python -m stage3_fastapi.stage3_demo
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
- ✅ **Comprehensive Testing**: Modüler test yapısı
- ✅ **Modern Python**: Type hints, async/await, Pydantic
- ✅ **Production Ready**: Logging, error handling, validation
- 🔄 **Future Ready**: SQLite ve Docker için stage3_plus hazır

## 🎓 Öğrenilen Teknolojiler

- **OOP**: Sınıflar, inheritance, encapsulation
- **API Integration**: REST API'ler, HTTP clients, error handling  
- **Web Development**: FastAPI, async programming, OpenAPI
- **Testing**: pytest, fixtures, mocking, test-driven development
- **Data Validation**: Pydantic modelleri, type checking
- **Documentation**: Swagger/OpenAPI, kod dokümantasyonu
- **Frontend Development**: HTML/CSS/JavaScript, API consumption
- **Containerization**: Docker (stage3_plus'ta planlanıyor)
- **Database**: SQLite (stage3_plus'ta planlanıyor)
- **Infrastructure**: Production deployment patterns

## 🐳 Docker Durumu ve SQLite Planı

### 📋 Mevcut Durum (Stage 3 - JSON Tabanlı)

**Stage 3 FastAPI** şu anda **JSON dosya tabanlı** bir kütüphane yönetim sistemi olarak çalışmaktadır:

- ✅ **FastAPI**: REST API tamamen fonksiyonel
- ✅ **JSON Kalıcılık**: `library.json` dosyasında veri saklama
- ✅ **Web Arayüzü**: Bootstrap 5 ile modern frontend
- ✅ **Test Edilmiş**: Comprehensive testler çalışıyor
- ❌ **Docker**: Henüz implement edilmemiş
- ❌ **SQLite**: Henüz implement edilmemiş

### 🚀 Gelecek Planları (Stage 3+ / Stage 3 Plus)

**Stage 3 Plus** klasöründe geliştirilecek özellikler:

1. **🗄️ SQLite Veritabanı**
   - JSON'dan SQLite'a geçiş
   - Database schema migration
   - ORM entegrasyonu (SQLAlchemy)

2. **🐳 Docker Implementation**
   - Multi-stage Dockerfile
   - Docker Compose orchestration
   - Volume mounting for database
   - Production-ready configuration

3. **🔧 Infrastructure**
   - Health checks
   - Logging configuration
   - Environment variables
   - Database connection pooling

### 📁 Proje Dizin Yapısı

```text
stage3_fastapi/        # Mevcut JSON tabanlı sistem
├── api.py            # FastAPI uygulaması
├── models.py         # Pydantic modelleri
├── library.py        # JSON tabanlı kütüphane
├── library.json      # Veri dosyası
└── static/           # Web arayüzü

stage3_plus/          # Gelecekteki SQLite + Docker
├── [ileride SQLite ve Docker entegrasyonu]
└── [gelişmiş özellikler buraya eklenecek]
```

### 💡 Mevcut Kullanım

Stage 3 sistemini kullanmak için:

```bash
# API'yi başlat
uvicorn stage3_fastapi.api:app --reload

# Web arayüzü: http://127.0.0.1:8000/static/index.html
# API docs: http://127.0.0.1:8000/docs
```

## 🚀 İleri Seviye Özellikler

### ✅ Tamamlanmış Geliştirmeler (Stage 3 - JSON Tabanlı)

- **🔄 PUT Endpoint**: Kitap güncelleme API'si
- **🌐 Web Frontend**: Modern HTML/CSS/JS arayüzü
- **📱 Responsive**: Mobil uyumlu tasarım
- **🔒 CORS**: Frontend-backend entegrasyonu
- **⚡ Real-time**: Canlı veri güncellemeleri
- **📦 JSON Storage**: Güvenilir dosya tabanlı kalıcılık

### 🚀 Gelecek Geliştirmeler (Stage 3+ - SQLite + Docker)

- **🗄️ SQLite Database**: İlişkisel veritabanı geçişi
- **🐳 Docker**: Container ve orchestration


### 🎨 Stage 3+ Ek İyileştirmeler (Ağustos 2025)

#### 📚 Kitap Tipleri ve Özel Alanlar

- **🎧 Audio Book Desteği**: Narrator ve süre bilgileri
- **💻 Digital Book Desteği**: Dosya boyutu ve format bilgileri  
- **📖 Physical Book Desteği**: Raf konumu bilgileri
- **🔄 Tip Değiştirme**: Kitap tipini edit ile değiştirme
- **📊 Tip Bazlı İstatistikler**: Audio, Digital, Physical sayıları

#### 🎨 Modern UI/UX İyileştirmeleri

- **🌈 Gelişmiş Tasarım**: Gradient renkler, animasyonlar
- **📊 Güzel İstatistikler**: Renkli kartlar, hover efektleri
- **🔍 Gelişmiş Arama**: Kitap tipi filtresi, card görünümü
- **✏️ Modal Edit**: Popup ile kitap düzenleme
- **📄 Sayfalama**: Gelişmiş pagination, sayfa numarası seçimi

#### 🛠️ İşlevsellik İyileştirmeleri

- **📝 Manuel Ekleme**: Tüm kitap tiplerini destekler
- **🔧 ISBN Ekleme**: Kitap tipi seçimi ile ekleme
- **🔄 Borrow/Return**: Arama sonuçlarında da çalışır
- **🎯 Filtreleme**: Tüm sayfalarda çalışan filtreler
- **⚡ Canlı Güncelleme**: Anlık veri senkronizasyonu

#### 🎯 API Geliştirmeleri

- **📦 Genişletilmiş Model**: Tüm kitap tiplerini destekler
- **🔄 PUT Endpoint**: Tüm alanları günceller
- **✅ Validation**: Pydantic ile gelişmiş doğrulama
- **📊 Response Model**: Zengin kitap verileri

---

**Proje**: Global AI Hub Python 202 Bootcamp Final Project  
**Geliştirici**: [ufukzkn](https://github.com/ufukzkn)  
**Teknolojiler**: Python 3.13 • FastAPI • pytest • Open Library API

---
