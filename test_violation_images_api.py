#!/usr/bin/env python3
"""
Test script for the new violation images API endpoint
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:5000/api"

def test_violation_images_api():
    """Test the violation images API with various parameters"""
    
    print("🧪 Testing Violation Images API")
    print("=" * 50)
    
    # Test 1: Get all violation images (no filters)
    print("\n1. Testing: Get all violation images")
    try:
        response = requests.get(f"{API_BASE_URL}/violation_images")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} violation images")
            if data:
                print(f"   Sample image: {data[0]['filename']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Get violation images for today
    print("\n2. Testing: Get violation images for today")
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        response = requests.get(f"{API_BASE_URL}/violation_images?date={today}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} violation images for {today}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Get violation images with time range
    print("\n3. Testing: Get violation images with time range")
    try:
        response = requests.get(f"{API_BASE_URL}/violation_images?date={today}&time_from=07:00&time_to=08:00")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} violation images for {today} 07:00-08:00")
            if data:
                for img in data[:3]:  # Show first 3 images
                    print(f"     - {img['filename']} ({img['timestamp']})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: Test image serving endpoint
    print("\n4. Testing: Image serving endpoint")
    try:
        # First get a violation image to test
        response = requests.get(f"{API_BASE_URL}/violation_images")
        if response.status_code == 200:
            data = response.json()
            if data:
                test_image = data[0]
                image_url = f"http://localhost:5000/violations/{test_image['file_path']}"
                print(f"   Testing image URL: {image_url}")
                
                img_response = requests.head(image_url)
                print(f"   Image Status: {img_response.status_code}")
                if img_response.status_code == 200:
                    print(f"   Content-Type: {img_response.headers.get('Content-Type', 'Unknown')}")
                else:
                    print(f"   Image Error: Failed to fetch image")
            else:
                print("   No violation images available to test")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Violation Images API Test Complete")

if __name__ == "__main__":
    test_violation_images_api()
