#!/usr/bin/env python3
"""
Test all IP camera routes to see which ones work.
"""

import requests

def test_route(domain, name):
    url = f"http://localhost:5000/ipcamera_stable/{domain}"
    print(f"\nTesting {name} ({domain}):")
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
    print("Testing all IP camera domain routes...")
    
    routes = [
        ("general", "General"),
        ("healthcare", "Healthcare"), 
        ("manufacturing", "Manufacturing"),
        ("construction", "Construction"),
        ("oilgas", "Oil & Gas")
    ]
    
    results = []
    for domain, name in routes:
        result = test_route(domain, name)
        results.append((name, result))
    
    print("\n" + "="*50)
    print("RESULTS SUMMARY:")
    print("="*50)
    for name, success in results:
        status = "✅ Working" if success else "❌ Failed"
        print(f"{status} - {name}")
    
    working_count = sum(1 for _, success in results if success)
    if working_count == 0:
        print(f"\n🔍 DIAGNOSIS: No IP camera routes are working.")
        print("This suggests:")
        print("1. No physical IP camera is connected")
        print("2. Camera IP/credentials are wrong") 
        print("3. Camera is not accessible from this network")
        print("\n💡 SOLUTION: Use webcam feeds instead, or connect a real IP camera")
    elif working_count < len(results):
        print(f"\n🔍 DIAGNOSIS: Some routes work ({working_count}/{len(results)})")
        print("This suggests a domain-specific issue")
    else:
        print(f"\n✅ All routes working! The issue might be in React.")

if __name__ == "__main__":
    main()
