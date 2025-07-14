#!/usr/bin/env python3
"""
Debug the confidence extraction by checking the exact matching parameters
"""
import requests
import json

def debug_confidence_matching():
    """Get a single violation and see what the Flask app is trying to match."""
    print("🔍 Debugging Confidence Matching")
    print("=" * 50)
    
    # Get one violation to see the debug output
    response = requests.get(
        "http://localhost:5000/api/violation_images",
        params={
            'date': '2025-07-14',
            'time_from': '07:45',
            'time_to': '07:45'
        }
    )
    
    if response.status_code == 200:
        violations = response.json()
        if violations:
            violation = violations[0]
            print(f"📸 Sample violation:")
            print(f"   Filename: {violation['filename']}")
            print(f"   Timestamp: {violation['timestamp']}")
            print(f"   Domain: {violation['camera_location']}")
            print(f"   Confidence: {violation['confidence']}")
            
            # Extract timestamp components
            filename = violation['filename']
            # violation_Manufacturing_20250714_074500_000000.jpg
            parts = filename.split('_')
            if len(parts) >= 4:
                date_part = parts[2]  # 20250714
                time_part = parts[3]  # 074500
                print(f"\n🔍 Filename parsing:")
                print(f"   Date part: {date_part}")
                print(f"   Time part: {time_part}")
                
                # Convert to timestamp format that should be searched
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                second = time_part[4:6]
                
                search_timestamp = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                print(f"   Search timestamp: {search_timestamp}")
        else:
            print("❌ No violations found")
    else:
        print(f"❌ API request failed: {response.status_code}")

if __name__ == "__main__":
    debug_confidence_matching()
