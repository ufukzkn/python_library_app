"""
Stage 3 FastAPI Test - Basit Çalıştırma Testi
"""


# Önce mevcut API dosyasını kontrol et
print("=== Stage 3 FastAPI Files Check ===")

import os
stage3_dir = os.path.dirname(__file__)
print(f"Current directory: {os.getcwd()}")

def check_file(filename):
    path = os.path.join(stage3_dir, filename)
    if os.path.exists(path):
        print(f"✓ {filename} found")
    else:
        print(f"✗ {filename} not found")

check_file("api.py")
check_file("models.py")
check_file("library.py")

print("\n=== Import Test ===")


try:
    from stage3_fastapi.models import Book, ISBNRequest, BookResponse
    print("✓ Models imported successfully")
except Exception as e:
    print(f"✗ Models import failed: {e}")

try:
    from stage3_fastapi.library import Library
    print("✓ Library imported successfully")
except Exception as e:
    print(f"✗ Library import failed: {e}")

try:
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
except Exception as e:
    print(f"✗ FastAPI import failed: {e}")

try:
    from stage3_fastapi.api import app
    print("✓ API app imported successfully")
    print(f"✓ App type: {type(app)}")
    print(f"✓ App title: {app.title}")
except Exception as e:
    print(f"✗ API app import failed: {e}")

print("\n=== FastAPI Manual Test ===")

try:
    # Test a basic endpoint without running the server
    from fastapi.testclient import TestClient
    from stage3_fastapi.api import app

    client = TestClient(app)
    response = client.get("/")
    print(f"✓ Root endpoint response: {response.status_code}")
    print(f"✓ Response data: {response.json()}")

    # Test health endpoint
    health_response = client.get("/health")
    print(f"✓ Health endpoint response: {health_response.status_code}")
    print(f"✓ Health data: {health_response.json()}")

except Exception as e:
    print(f"✗ Manual test failed: {e}")

print("\n=== Stage 3 Ready! ===")
print("To start the API server:")
print("uvicorn api:app --reload --host 127.0.0.1 --port 8000")
print("Then visit: http://127.0.0.1:8000/docs")
