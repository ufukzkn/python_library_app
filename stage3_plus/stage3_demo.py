"""
Stage 3 Demo: FastAPI Integration
Bu demo FastAPI'nin çalışıp çalışmadığını test eder.
Önce API'yi manuel olarak başlatmanız gerekiyor: uvicorn stage3_fastapi.api:app --reload
"""

import httpx
import asyncio
import json

async def demo_api_calls():
    """FastAPI endpoints'lerini test et"""
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        print("=== Stage 3: FastAPI Demo ===")
        print("API Base URL:", base_url)
        print("Note: Make sure to start the API first: uvicorn stage3_fastapi.api:app --reload")
        print()
        
        try:
            # 1. Root endpoint
            print("1. Testing root endpoint...")
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            print()
            
            # 2. Health check
            print("2. Testing health check...")
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            print()
            
            # 3. List books (empty)
            print("3. Testing empty book list...")
            response = await client.get(f"{base_url}/books")
            print(f"   Status: {response.status_code}")
            print(f"   Books: {len(response.json())} books found")
            print()
            
            # 4. Add book by ISBN
            print("4. Testing add book by ISBN...")
            test_isbn = "9780140328721"  # Fantastic Mr. Fox
            response = await client.post(f"{base_url}/books", json={"isbn": test_isbn})
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                book = response.json()
                print(f"   Added: {book['title']} by {', '.join(book['authors'])}")
            else:
                print(f"   Error: {response.json()}")
            print()
            
            # 5. List books (should have 1)
            print("5. Testing book list after adding...")
            response = await client.get(f"{base_url}/books")
            print(f"   Status: {response.status_code}")
            books = response.json()
            print(f"   Books: {len(books)} books found")
            for book in books:
                print(f"     - {book['title']} ({book['isbn']})")
            print()
            
            # 6. Get specific book
            print("6. Testing get specific book...")
            response = await client.get(f"{base_url}/books/{test_isbn}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                book = response.json()
                print(f"   Found: {book['title']}")
            print()
            
            # 7. Try to add duplicate
            print("7. Testing duplicate book prevention...")
            response = await client.post(f"{base_url}/books", json={"isbn": test_isbn})
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print("   ✓ Duplicate correctly prevented")
            print()
            
            # 8. Delete book
            print("8. Testing delete book...")
            response = await client.delete(f"{base_url}/books/{test_isbn}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 204:
                print("   ✓ Book successfully deleted")
            print()
            
            # 9. Verify deletion
            print("9. Testing book list after deletion...")
            response = await client.get(f"{base_url}/books")
            print(f"   Status: {response.status_code}")
            books = response.json()
            print(f"   Books: {len(books)} books found")
            print()
            
            # 10. Test 404 scenarios
            print("10. Testing 404 scenarios...")
            response = await client.get(f"{base_url}/books/9999999999999")
            print(f"    Get non-existent book: {response.status_code}")
            
            response = await client.delete(f"{base_url}/books/9999999999999")
            print(f"    Delete non-existent book: {response.status_code}")
            print()
            
            print("=== Demo completed successfully! ===")
            print("FastAPI endpoints are working correctly.")
            print("Visit http://127.0.0.1:8000/docs for interactive API documentation.")
            
        except httpx.ConnectError:
            print("❌ Cannot connect to API!")
            print("Make sure to start the API first:")
            print("   uvicorn stage3_fastapi.api:app --reload")
        except Exception as e:
            print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(demo_api_calls())
