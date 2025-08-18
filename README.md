# Global AI Hub Python 202 Bootcamp Proje

Bu depo, 3 aşamalı bir OOP projesini içerir:
- stage1_oop: Temel OOP + JSON kalıcılık + birim testleri
- stage2_oop: (Plan) Gelişmiş özellikler
- stage3_oop: (Plan) Son dokunuşlar ve entegrasyon

## Proje Yapısı
```
python_oop_kutuphane/
├─ stage1_oop/
│  ├─ __init__.py
│  ├─ models.py           # Book dataclass (to_dict/from_dict)
│  ├─ library.py          # Library: add/list/find/remove + JSON kalıcılık
│  └─ tests/
│     └─ test_library.py  # Birim testleri (pytest)
├─ pytest.ini             # [pytest] pythonpath = .
├─ requirements.txt
└─ README.md
```

## Kurulum (uv ile)
Windows PowerShell:
```powershell
# Sanal ortam
uv venv
.\.venv\Scripts\Activate.ps1

# Bağımlılıklar
uv pip install -r requirements.txt
# veya
uv pip install pytest pydantic
```

Not: PowerShell script engeli varsa:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Test Çalıştırma
Kök dizinden:
```powershell
pytest -q
# veya aktivasyonsuz:
uv run pytest -q
```

## Stage 1 Özeti
- Book: title, author, isbn alanları; to_dict()/from_dict() ile serileştirme.
- Library:
  - add_book(book) -> bool (aynı ISBN ikinci kez eklenemez)
  - list_books() -> iterator
  - find_book(isbn) -> Book | None
  - remove_book(isbn) -> bool
  - Kalıcılık: JSON dosyası. Varsayılan ad `lib.json`; istenirse `Library(filename=Path("data/library.json"))` ile özelleştirilebilir.
  - Bozuk JSON dosyası yüklemeyi bozmaz; güvenli fallback.

## Stage 2 ve 3
- Bu aşamalar için gereksinimler belirlendikçe ilgili klasörlerde kod ve testler eklenecektir.
- README bu bölümler genişledikçe güncellenecektir.

## Sorun Giderme
- `ModuleNotFoundError: stage1_oop`: Kökten çalıştırın ve `stage1_oop/__init__.py` olduğundan emin olun.
- `pytest.ini ... '\ufeff[pytest]'`: Dosyayı BOM olmadan UTF-8 olarak kaydedin.
- Venv aktivasyonu: `.\.venv\Scripts\Activate.ps1`