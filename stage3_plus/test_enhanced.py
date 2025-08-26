"""
Stage 3 API Test - PUT endpoint ve Frontend test
"""

import json
import requests
from fastapi.testclient import TestClient

def test_api_endpoints():
    """Test all API endpoints including PUT"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Stage 3 Enhanced API Test ===")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"✓ Health check: {response.status_code}")
        
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        data = response.json()
        print(f"✓ Root endpoint: {response.status_code}")
        print(f"✓ Features: {data.get('features', [])}")
        
        # Test adding a book
        test_isbn = "9780140449136"
        response = requests.post(f"{base_url}/books", 
                               json={"isbn": test_isbn})
        if response.status_code == 201:
            print(f"✓ Book added: {response.status_code}")
            book_data = response.json()
            print(f"  Title: {book_data.get('title')}")
        else:
            print(f"⚠ Book already exists or error: {response.status_code}")
        
        # Test GET book
        response = requests.get(f"{base_url}/books/{test_isbn}")
        if response.status_code == 200:
            print(f"✓ Book retrieved: {response.status_code}")
            book_data = response.json()
            original_title = book_data.get('title')
            print(f"  Original title: {original_title}")
        
        # Test PUT (Update) book
        update_data = {
            "title": f"{original_title} - Updated",
            "is_borrowed": True
        }
        response = requests.put(f"{base_url}/books/{test_isbn}", 
                              json=update_data)
        if response.status_code == 200:
            print(f"✓ Book updated: {response.status_code}")
            updated_book = response.json()
            print(f"  Updated title: {updated_book.get('title')}")
            print(f"  Borrowed status: {updated_book.get('is_borrowed')}")
        else:
            print(f"✗ Update failed: {response.status_code}")
        
        # Test listing books
        response = requests.get(f"{base_url}/books")
        if response.status_code == 200:
            books = response.json()
            print(f"✓ Books listed: {len(books)} books found")
        
        print("\n=== Frontend Files Check ===")
        import os
        static_dir = "static"
        files_to_check = ["index.html", "style.css", "script.js"]
        
        for file in files_to_check:
            file_path = os.path.join(static_dir, file)
            if os.path.exists(file_path):
                print(f"✓ {file} found")
            else:
                print(f"✗ {file} not found")
        
        print("\n=== Docker Files Check ===")
        docker_files = ["Dockerfile", "docker-compose.yml", ".dockerignore"]
        
        for file in docker_files:
            if os.path.exists(file):
                print(f"✓ {file} found")
            else:
                print(f"✗ {file} not found")
        
    except requests.exceptions.ConnectionError:
        print("✗ API is not running. Please start with: uvicorn stage3_fastapi.api:app --reload")
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
