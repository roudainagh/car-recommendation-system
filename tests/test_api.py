import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_server(timeout=30):
    """Wait for server to start"""
    print("⏳ Waiting for server to start...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ Server did not start within timeout")
    return False

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Health check: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_recommend_by_user():
    """Test recommendations by user ID"""
    payload = {
        "user_id": 1,
        "top_n": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/recommend/by-user",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Got {data['total_found']} recommendations for user 1")
            for i, car in enumerate(data['recommendations'], 1):
                print(f"   {i}. {car['brand']} {car['model']}: {car['similarity_score']}%")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_recommend_by_preferences():
    """Test recommendations by preferences"""
    payload = {
        "budget_max": 40000,
        "min_required_seats": 5,
        "carrosserie_preferee": "SUV",
        "energie_preferee": "Hybride",
        "boite_preferee": "Automatique",
        "importance_consommation": 4,
        "importance_performance": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/recommend/by-preferences?top_n=3",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Got {data['total_found']} recommendations for preferences")
            for i, car in enumerate(data['recommendations'], 1):
                print(f"   {i}. {car['brand']} {car['model']}: {car['similarity_score']}%")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_search_cars():
    """Test car search"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/cars/search",
            params={"query": "audi", "limit": 3},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Found {data['total_found']} cars matching 'audi'")
            for car in data['results']:
                print(f"   - {car['brand']} {car['model']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_get_features():
    """Test get features endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/features", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Got features: {list(data.keys())}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 TESTING FASTAPI ENDPOINTS")
    print("="*60)
    
    # Wait for server
    if not wait_for_server():
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Get Features", test_get_features),
        ("Search Cars", test_search_cars),
        ("Recommend by User", test_recommend_by_user),
        ("Recommend by Preferences", test_recommend_by_preferences),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing: {name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((name, "✅ PASSED" if success else "❌ FAILED"))
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            results.append((name, "❌ ERROR"))
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    for name, result in results:
        print(f"{result} - {name}")