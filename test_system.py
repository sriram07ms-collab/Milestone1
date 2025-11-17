"""Quick system test for frontend and backend"""
import requests
import sys
import time

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend():
    """Test backend health and chat endpoint"""
    print("=" * 50)
    print("Testing Backend...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("\n1. Testing /api/health...")
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database_connected')}")
            print(f"   LLM: {data.get('llm_configured')}")
            print(f"   RAG: {data.get('rag_configured')}")
        else:
            print(f"   [FAIL] Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   [FAIL] Cannot connect to backend at {BACKEND_URL}")
        print("   Make sure the backend server is running!")
        return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False
    
    # Test chat endpoint
    try:
        print("\n2. Testing /api/chat...")
        test_query = {
            "query": "What is ICICI Prudential Large Cap Fund?"
        }
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=test_query,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Chat endpoint working")
            print(f"   Answer: {data.get('answer', '')[:100]}...")
            return True
        else:
            print(f"   [FAIL] Chat endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_frontend():
    """Test if frontend is accessible"""
    print("\n" + "=" * 50)
    print("Testing Frontend...")
    print("=" * 50)
    
    try:
        print("\n1. Testing frontend accessibility...")
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"   [OK] Frontend is accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"   [FAIL] Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   [FAIL] Cannot connect to frontend at {FRONTEND_URL}")
        print("   Make sure the frontend dev server is running!")
        return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("SYSTEM TEST")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Backend:  {'[PASS]' if backend_ok else '[FAIL]'}")
    print(f"Frontend: {'[PASS]' if frontend_ok else '[FAIL]'}")
    
    if backend_ok and frontend_ok:
        print("\n[SUCCESS] All systems operational!")
        sys.exit(0)
    else:
        print("\n[ERROR] Some tests failed. Please check the errors above.")
        sys.exit(1)

