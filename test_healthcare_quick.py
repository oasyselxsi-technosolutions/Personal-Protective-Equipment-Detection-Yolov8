#!/usr/bin/env python3
"""
Quick test to check if healthcare route is responding.
"""

import requests
import time

def test_healthcare_route():
    print("Testing healthcare route...")
    
    url = "http://localhost:5000/ipcamera_stable/healthcare"
    print(f"URL: {url}")
    
    try:
        print("Sending request...")
        response = requests.get(url, timeout=10, stream=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Route responding with 200")
            
            # Try to read some content
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            
            if 'multipart/x-mixed-replace' in content_type:
                print("✅ Correct MJPEG content type")
                
                # Read first chunk
                try:
                    first_chunk = next(response.iter_content(chunk_size=1024), None)
                    if first_chunk:
                        print(f"✅ Got content: {len(first_chunk)} bytes")
                        print(f"First 50 bytes: {first_chunk[:50]}")
                    else:
                        print("❌ No content received")
                except Exception as e:
                    print(f"❌ Error reading content: {e}")
            else:
                print(f"❌ Wrong content type. Response: {response.text[:200]}")
        else:
            print(f"❌ Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_healthcare_route()
