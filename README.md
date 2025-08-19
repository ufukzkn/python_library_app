# Global AI Hub Python 202 Bootcamp Projesi

Bu depo, adım adım geliştirilen 3 aşamalı bir kütüphane yönetim sistemi projesini içerir:

- **Stage 1**: Temel OOP yapısı + JSON kalıcılık + birim testleri
- **Stage 2**: API entegrasyonu (Open Library) + hata yönetimi
- **Stage 3**: (Planlanan) Son dokunuşlar ve iyileştirmeler

## Proje Yapısı

```
python_oop_kutuphane/
├─ stage1_oop/                  # Aşama 1: Temel OOP
│  ├─ models.py                 # Book veri sınıfı
│  ├─ library.py                # Kütüphane yönetimi + JSON
│  ├─ main.py                   # CLI arayüzü
│  └─ tests/                    # Birim testleri
│     └─ test_library.py
│
├─ stage2_api/                  # Aşama 2: API Entegrasyonu
│  ├─ models.py                 # Geliştirilmiş Book modeli
│  ├─ library.py                # API entegrasyonu + httpx
│  ├─ main.py                   # Gelişmiş CLI (ISBN API desteği)
│  ├─ stage2_demo.py            # Demo: Stage 1 ve 2 özellikleri
│  └─ tests/
│     └─ test_library_api.py
│
├─ pytest.ini                   # Test yapılandırması
├─ requirements.txt             # Proje bağımlılıkları
└─ README.md                    # Bu dosya
```

## Kurulum

Windows PowerShell ile kurulum:

```powershell
# Sanal ortam oluşturma
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Bağımlılıklar
pip install -r requirements.txt
```

Not: PowerShell'de script çalıştırma sorunu yaşarsanız:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Çalıştırma

### Stage 1 (Temel Kütüphane)
```powershell
py -m stage1_oop.main
```

### Stage 2 (API Entegrasyonu)
```powershell
# CLI Arayüzü
py -m stage2_api.main

# Demo Script (Stage 1 ve Stage 2 özelliklerini test eder)
py -m stage2_api.stage2_demo
```

**Demo Script Açıklaması:**
- `stage2_demo.py` hem Stage 1 hem de Stage 2 özelliklerini test eder
- **Oluşturduğu dosyalar:**
  - `stage1_demo.json`: Manuel kitap ekleme testi (Stage 1 uyumluluğu)
  - `stage2_demo.json`: API ile kitap ekleme testi (Stage 2 özellikleri)
     (Demoyu bu 2 json dosyasının içini boşaltarak deneyebilirsiniz)
- **Test senaryoları:**
    
  - Stage 1 uyumluluğu: Manuel kitap ekleme
  - Stage 2 API: ISBN ile otomatik kitap ekleme
  - Hata yönetimi: Geçersiz ISBN testi

## Test Etme

```powershell
# Tüm testler
pytest -q

# Sadece Stage 1 testleri
pytest -q stage1_oop/tests

# Sadece Stage 2 testleri
pytest -q stage2_api/tests
```

## Stage 1: Temel OOP Özellikleri

- **Book** sınıfı:
  - Alanlar: title, author, isbn
  - JSON serileştirme: to_dict() / from_dict()

- **Library** sınıfı:
  - `add_book(book)`: Kitap ekleme (aynı ISBN tekrar eklenemez)
  - `list_books()`: Tüm kitapları listeleme
  - `find_book(isbn)`: ISBN ile kitap bulma
  - `remove_book(isbn)`: Kitap silme
  - JSON dosya kalıcılığı (varsayılan: lib.json)
  - Güvenli dosya işlemleri (bozuk JSON için fallback)

## Stage 2: API Entegrasyonu

- **Open Library API** entegrasyonu:
  - `add_book(isbn)`: ISBN ile otomatik kitap ekleme
  - API URL: https://openlibrary.org/isbn/{isbn}.json
  
- **Yeni Özellikler**:
  - httpx ile HTTP istekleri
  - Kitap bilgilerini API'den otomatik çekme
  - Güçlü hata yönetimi (ağ hatası, 404, eksik veri)
  - Redirect yönetimi ve timeout
  - Stage 1 ile tam uyumluluk (manuel kitap ekleme hala mevcut)

- **CLI Menüsü**:
  ```
  [1] Add book manually (Stage 1 style)
  [2] Add book by ISBN from API (Stage 2 style)
  [3] Remove
  [4] List
  [5] Find by ISBN
  [0] Exit
  ```

## Stage 3: Planlanan Geliştirmeler

- Daha fazla API entegrasyonu
- Kullanıcı arayüzü iyileştirmeleri
- Gelişmiş arama özellikleri
- Performans optimizasyonları