#!/usr/bin/env python3
"""
Quick test script to verify the Flask routes are working
"""

import requests
import time

def test_routes():
    """Test the available routes"""
    base_url = "http://localhost:5000"
    
    routes_to_test = [
        "/api/dashboard",
        "/ipcamera_stable",
        "/ipcamera_stable_raw", 
        "/ipcamera_stable/general",
        "/ipcamera_stable/manufacturing",
        "/ipcamera_stable/construction",
        "/ipcamera_stable/healthcare",
        "/ipcamera_stable/oilgas",
        "/ipcamera_manufacturing",
        "/ipcamera_construction",
        "/ipcamera_healthcare",
        "/ipcamera_oilgas"
    ]
    
    print("🔍 Testing Flask Routes")
    print("=" * 50)
    
    for route in routes_to_test:
        url = f"{base_url}{route}"
        try:
            # Use HEAD request to avoid actually streaming video
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {route} - OK (200)")
            elif response.status_code == 404:
                print(f"❌ {route} - Not Found (404)")
            elif response.status_code == 500:
                print(f"⚠️  {route} - Server Error (500)")
            else:
                print(f"🔶 {route} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 {route} - Server not running")
        except requests.exceptions.Timeout:
            print(f"⏰ {route} - Timeout (might be normal for video streams)")
        except Exception as e:
            print(f"❓ {route} - Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Route testing complete!")
    print("\n💡 Note: Video stream routes may timeout or show errors")
    print("   without a camera connected, but should not return 404.")

if __name__ == "__main__":
    print("⚠️  Make sure Flask server is running first!")
    print("   Run: python flaskapp.py")
    print("   Then run this test in another terminal\n")
    
    input("Press Enter when server is ready...")
    test_routes()
