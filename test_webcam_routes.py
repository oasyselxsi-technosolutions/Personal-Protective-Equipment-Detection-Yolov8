#!/usr/bin/env python3
"""
Test webcam routes to see if they work.
"""

import requests

def test_webcam_route(endpoint, name):
    url = f"http://localhost:5000/api/{endpoint}"
    print(f"\nTesting {name}:")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=5, stream=True)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ {name} - Working")
            return True
        else:
            print(f"❌ {name} - Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {name} - Exception: {e}")
        return False

def main():
    print("Testing webcam routes...")
    
    routes = [
        ("webcam_raw", "Webcam Raw"),
        ("webcam_yolo", "Webcam YOLO"), 
        ("webcam_healthcare", "Webcam Healthcare"),
        ("webcam_manufacturing", "Webcam Manufacturing"),
        ("webcam_construction", "Webcam Construction"),
        ("webcam_oilgas", "Webcam Oil & Gas")
    ]
    
    results = []
    for endpoint, name in routes:
        result = test_webcam_route(endpoint, name)
        results.append((name, result))
    
    print("\n" + "="*50)
    print("WEBCAM RESULTS SUMMARY:")
    print("="*50)
    for name, success in results:
        status = "✅ Working" if success else "❌ Failed"
        print(f"{status} - {name}")
    
    working_count = sum(1 for _, success in results if success)
    print(f"\nWorking routes: {working_count}/{len(results)}")

if __name__ == "__main__":
    main()
