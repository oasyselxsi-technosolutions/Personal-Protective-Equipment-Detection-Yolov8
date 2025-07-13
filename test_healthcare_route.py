#!/usr/bin/env python3
"""
Test script to debug the healthcare IP camera feed issue.
This script will test the healthcare route and provide detailed diagnostics.
"""

import requests
import time
import sys
import os
from datetime import datetime

def test_healthcare_route():
    """Test the healthcare IP camera route with detailed diagnostics."""
    
    print("="*80)
    print("HEALTHCARE IP CAMERA FEED DIAGNOSTICS")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    base_url = "http://localhost:5000"
    healthcare_url = f"{base_url}/ipcamera_stable/healthcare"
    
    print(f"Testing URL: {healthcare_url}")
    print()
    
    # Test 1: Basic connectivity
    print("1. Testing basic Flask server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   ✅ Flask server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("   ❌ Flask server is not running or not accessible")
        print("   💡 Make sure to start the Flask app with: python flaskapp.py 5000")
        return False
    except Exception as e:
        print(f"   ❌ Error connecting to Flask server: {e}")
        return False
    
    # Test 2: Test the healthcare route specifically
    print("\n2. Testing healthcare route...")
    try:
        print(f"   Sending GET request to: {healthcare_url}")
        response = requests.get(healthcare_url, timeout=15, stream=True)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Route responds with 200 OK")
            
            # Check if it's actually streaming content
            content_type = response.headers.get('Content-Type', '')
            if 'multipart/x-mixed-replace' in content_type:
                print("   ✅ Correct MJPEG streaming content type")
                
                # Try to read some content
                try:
                    chunk_count = 0
                    total_bytes = 0
                    start_time = time.time()
                    
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            chunk_count += 1
                            total_bytes += len(chunk)
                            
                            if chunk_count == 1:
                                print(f"   ✅ First chunk received ({len(chunk)} bytes)")
                                print(f"   📊 First few bytes: {chunk[:50]}")
                                
                            # Stop after a few chunks or 10 seconds
                            if chunk_count >= 5 or time.time() - start_time > 10:
                                break
                    
                    print(f"   ✅ Stream is active: {chunk_count} chunks, {total_bytes} bytes in {time.time() - start_time:.1f}s")
                    
                except Exception as stream_error:
                    print(f"   ⚠️ Error reading stream content: {stream_error}")
                    
            else:
                print(f"   ⚠️ Unexpected content type: {content_type}")
                # Try to read response as text
                try:
                    text_content = response.text[:500]
                    print(f"   📄 Response content (first 500 chars): {text_content}")
                except:
                    print("   ❌ Could not read response content")
                    
        elif response.status_code == 500:
            print("   ❌ Server error (500)")
            try:
                error_content = response.json()
                print(f"   📄 Error details: {error_content}")
            except:
                print(f"   📄 Raw error response: {response.text[:500]}")
                
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   📄 Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (15 seconds)")
        print("   💡 This might indicate the route is hanging or camera connection issues")
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - server might have crashed")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test other domain routes for comparison
    print("\n3. Testing other domain routes for comparison...")
    other_domains = ['general', 'manufacturing', 'construction', 'oilgas']
    
    for domain in other_domains:
        domain_url = f"{base_url}/ipcamera_stable/{domain}"
        try:
            print(f"   Testing {domain}...")
            response = requests.get(domain_url, timeout=5, stream=True)
            
            if response.status_code == 200:
                # Just check if we get some content quickly
                try:
                    first_chunk = next(response.iter_content(chunk_size=1024), None)
                    if first_chunk:
                        print(f"     ✅ {domain}: Working ({len(first_chunk)} bytes)")
                    else:
                        print(f"     ⚠️ {domain}: No content")
                except:
                    print(f"     ⚠️ {domain}: Content read error")
            else:
                print(f"     ❌ {domain}: Status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"     ⏱️ {domain}: Timeout")
        except Exception as e:
            print(f"     ❌ {domain}: Error - {e}")
    
    # Test 4: Environment and configuration check
    print("\n4. Environment and configuration diagnostics...")
    print("   This would require access to the Flask app logs.")
    print("   💡 Check the logs/flaskapp.log file for detailed backend diagnostics")
    print("   💡 Look for lines containing '[HEALTHCARE]' in the logs")
    
    print("\n" + "="*80)
    print("DIAGNOSTICS COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Check the Flask app logs (logs/flaskapp.log) for backend errors")
    print("2. Verify camera connectivity and environment variables")
    print("3. Check React browser console for frontend errors")
    print("4. Ensure the YOLO model files are present")
    
    return True

if __name__ == "__main__":
    test_healthcare_route()
