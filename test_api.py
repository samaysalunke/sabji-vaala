"""
Test script to verify API functionality with mock data
Since Agmarknet might be slow/unavailable, we'll test with sample data
"""

import requests
import json
from datetime import datetime
import time

# Add some sample data to test the API
from src.database.price_db import PriceDatabase
from src.data.vegetables import list_supported_vegetables, list_supported_cities

def populate_test_data():
    """
    Add sample data to test the API
    """
    print("🌱 Populating test data...")
    
    db = PriceDatabase()
    
    test_data = [
        {
            "city": "mumbai",
            "vegetable": "tomato",
            "price": 25.50,
            "price_per": "kg",
            "min_price": 22.0,
            "max_price": 28.0,
            "market": "Mumbai Central Market",
            "currency": "INR",
            "source": "test_data"
        },
        {
            "city": "delhi",
            "vegetable": "tomato",
            "price": 30.00,
            "price_per": "kg",
            "market": "Azadpur Mandi",
            "currency": "INR",
            "source": "test_data"
        },
        {
            "city": "mumbai",
            "vegetable": "potato",
            "price": 18.75,
            "price_per": "kg",
            "market": "Vashi Market",
            "currency": "INR",
            "source": "test_data"
        },
        {
            "city": "bangalore",
            "vegetable": "onion",
            "price": 22.25,
            "price_per": "kg",
            "market": "Yeshwantpur Market", 
            "currency": "INR",
            "source": "test_data"
        }
    ]
    
    for data in test_data:
        success = db.insert_price(data)
        if success:
            print(f"✅ Added: {data['city']} {data['vegetable']} ₹{data['price']}")
        else:
            print(f"❌ Failed: {data['city']} {data['vegetable']}")
    
    db.close()
    print("✅ Test data populated!")

def test_api_endpoints():
    """
    Test all API endpoints
    """
    base_url = "http://localhost:8000"
    
    print(f"\n🧪 Testing API at {base_url}...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        health_data = response.json()
        print(f"   Status: {health_data['status']}")
        print(f"   DB Stats: {health_data['database_stats']}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test vegetables list
    try:
        response = requests.get(f"{base_url}/vegetables")
        print(f"✅ Vegetables endpoint: {response.status_code}")
        vegetables = response.json()
        print(f"   Supported vegetables: {vegetables[:5]}...")  # Show first 5
    except Exception as e:
        print(f"❌ Vegetables endpoint failed: {e}")
    
    # Test cities list
    try:
        response = requests.get(f"{base_url}/cities")
        print(f"✅ Cities endpoint: {response.status_code}")
        cities = response.json()
        print(f"   Supported cities: {cities}")
    except Exception as e:
        print(f"❌ Cities endpoint failed: {e}")
    
    # Test price endpoint with test data
    test_requests = [
        {"city": "Mumbai", "vegetable": "tomato"},
        {"city": "delhi", "vegetable": "tomato"},
        {"city": "mumbai", "vegetable": "potato"},
        {"city": "bangalore", "vegetable": "onion"},
        {"city": "mumbai", "vegetable": "unknown_vegetable"},  # Should fail
        {"city": "unknown_city", "vegetable": "tomato"}       # Should fail
    ]
    
    for req in test_requests:
        try:
            response = requests.post(
                f"{base_url}/price",
                json=req,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Price {req['city']} {req['vegetable']}: ₹{data['price']} ({data['cache_status']})")
            else:
                error = response.json()
                print(f"⚠️ Price {req['city']} {req['vegetable']}: {response.status_code} - {error.get('detail', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Price request failed: {e}")
    
    # Test city prices
    try:
        response = requests.get(f"{base_url}/city/mumbai/prices")
        if response.status_code == 200:
            prices = response.json()
            print(f"✅ Mumbai prices: {len(prices)} items")
            for price in prices:
                print(f"   {price['vegetable']}: ₹{price['price']}")
        else:
            print(f"⚠️ Mumbai prices: {response.status_code}")
    except Exception as e:
        print(f"❌ Mumbai prices failed: {e}")
    
    print("✅ API testing completed!")
    return True

if __name__ == "__main__":
    print("🚀 SabjiGPT API Test Suite")
    print("=" * 50)
    
    # First populate test data
    populate_test_data()
    
    # Give user instructions to start the server
    print(f"\n📋 To test the API:")
    print(f"1. In a new terminal, run:")
    print(f"   cd {'/Users/samaysalunke/Documents/everything-hobby/sabjiGPT'}")
    print(f"   source venv/bin/activate")
    print(f"   python -m uvicorn src.api.main:app --reload")
    print(f"2. Wait for server to start, then press Enter here...")
    
    input("Press Enter when the API server is running...")
    
    # Test the API
    test_api_endpoints()
    
    print(f"\n🌐 You can also test manually at:")
    print(f"   - API Docs: http://localhost:8000/docs")
    print(f"   - ReDoc: http://localhost:8000/redoc")
    print(f"   - Health: http://localhost:8000/health")
