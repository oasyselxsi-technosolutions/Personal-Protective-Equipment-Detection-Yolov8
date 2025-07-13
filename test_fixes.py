#!/usr/bin/env python3
"""
Test script to verify CORS and URL fixes for the healthcare feed issue.
Run this after restarting the Flask app to verify the fixes.
"""

import requests
import time
import json

def test_cors_fix():
    """Test that CORS is working properly."""
    print("="*60)
    print("TESTING CORS CONFIGURATION")
    print("="*60)
    
    # Test preflight OPTIONS request
    print("1. Testing preflight OPTIONS request...")
    try:
        response = requests.options(
            "http://localhost:5000/api/release_feed",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Check for duplicate headers
        origin_header = response.headers.get('Access-Control-Allow-Origin')
        if origin_header:
            if ',' in origin_header:
                print(f"   ❌ DUPLICATE ORIGIN HEADERS: {origin_header}")
                return False
            else:
                print(f"   ✅ Single origin header: {origin_header}")
        else:
            print("   ⚠️ No Access-Control-Allow-Origin header")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test actual POST request
    print("\n2. Testing actual POST request...")
    try:
        response = requests.post(
            "http://localhost:5000/api/release_feed",
            headers={
                'Origin': 'http://localhost:3000',
                'Content-Type': 'application/json'
            },
            json={"feed_type": "ipcamera"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ POST request successful")
        else:
            print(f"   ⚠️ POST returned {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def test_feed_urls():
    """Test that all feed URLs are accessible."""
    print("\n" + "="*60)
    print("TESTING FEED URL ACCESSIBILITY")
    print("="*60)
    
    urls_to_test = [
        ("General (with YOLO)", "http://localhost:5000/ipcamera_stable/general"),
        ("General (raw)", "http://localhost:5000/ipcamera_stable_raw/general"),
        ("Healthcare (with YOLO)", "http://localhost:5000/ipcamera_stable/healthcare"),
        ("Healthcare (raw)", "http://localhost:5000/ipcamera_stable_raw/healthcare"),
        ("Manufacturing", "http://localhost:5000/ipcamera_stable/manufacturing"),
        ("Construction", "http://localhost:5000/ipcamera_stable/construction"),
        ("Oil & Gas", "http://localhost:5000/ipcamera_stable/oilgas"),
    ]
    
    results = []
    
    for name, url in urls_to_test:
        print(f"\nTesting {name}: {url}")
        try:
            response = requests.get(url, timeout=10, stream=True)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('Content-Type', '')
                print(f"   Content-Type: {content_type}")
                
                if 'multipart/x-mixed-replace' in content_type:
                    # Try to read first chunk
                    try:
                        first_chunk = next(response.iter_content(chunk_size=1024), None)
                        if first_chunk:
                            print(f"   ✅ {name}: Working ({len(first_chunk)} bytes)")
                            results.append((name, "✅ Working"))
                        else:
                            print(f"   ⚠️ {name}: No content")
                            results.append((name, "⚠️ No content"))
                    except Exception as e:
                        print(f"   ❌ {name}: Read error - {e}")
                        results.append((name, f"❌ Read error"))
                else:
                    print(f"   ⚠️ {name}: Wrong content type")
                    results.append((name, "⚠️ Wrong content type"))
            else:
                print(f"   ❌ {name}: Status {response.status_code}")
                if response.status_code == 500:
                    try:
                        error_info = response.json()
                        print(f"   Error: {error_info.get('error', 'Unknown')}")
                    except:
                        pass
                results.append((name, f"❌ Status {response.status_code}"))
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️ {name}: Timeout")
            results.append((name, "⏱️ Timeout"))
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
            results.append((name, f"❌ Error"))
    
    # Summary
    print("\n" + "="*60)
    print("FEED URL TEST SUMMARY")
    print("="*60)
    for name, status in results:
        print(f"{status} {name}")
    
    return results

def test_react_config():
    """Test React configuration URLs."""
    print("\n" + "="*60)
    print("TESTING REACT CONFIG URLS")
    print("="*60)
    
    # Read the React config file
    try:
        with open("frontend/src/config/cameraFeedConfig.ts", "r") as f:
            config_content = f.read()
        
        print("✅ React config file accessible")
        
        # Extract URLs from config
        import re
        url_pattern = r'url: ["\']([^"\']+)["\']'
        urls = re.findall(url_pattern, config_content)
        
        print(f"Found {len(urls)} URLs in config:")
        for i, url in enumerate(urls, 1):
            print(f"   {i}. {url}")
            
        # Check for specific issues
        issues = []
        for url in urls:
            if "/general" in url and url.endswith("/general"):
                issues.append(f"⚠️ URL ends with /general (should be full path): {url}")
            if "localhost:5000" not in url and "127.0.0.1:5000" not in url:
                issues.append(f"⚠️ Non-local URL: {url}")
        
        if issues:
            print("\nConfiguration issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ No obvious configuration issues found")
            
    except Exception as e:
        print(f"❌ Error reading React config: {e}")

def main():
    print("FLASK APP FIXES VERIFICATION")
    print("="*80)
    print("This script verifies the CORS and URL fixes for the healthcare feed issue.")
    print("Make sure the Flask app is running before running this test.")
    print("="*80)
    
    # Test server connectivity first
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Flask server is running\n")
    except:
        print("❌ Flask server is not running. Please start it first.")
        print("   Command: python flaskapp.py 5000")
        return 1
    
    # Run tests
    cors_ok = test_cors_fix()
    feed_results = test_feed_urls()
    test_react_config()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL VERIFICATION SUMMARY")
    print("="*80)
    
    if cors_ok:
        print("✅ CORS configuration is working")
    else:
        print("❌ CORS configuration has issues")
    
    working_feeds = len([r for r in feed_results if "✅" in r[1]])
    total_feeds = len(feed_results)
    print(f"📊 Feed URLs: {working_feeds}/{total_feeds} working")
    
    if cors_ok and working_feeds > 0:
        print("\n🎉 Fixes appear to be working! Try the React app now.")
        print("   The CORS errors should be resolved.")
        print("   The healthcare feed should load properly.")
    else:
        print("\n🔧 Some issues remain. Check the logs for more details.")
    
    return 0

if __name__ == "__main__":
    exit(main())
