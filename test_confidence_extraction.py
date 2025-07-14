#!/usr/bin/env python3
"""
Test script to verify confidence extraction from detection_results.txt
"""
import requests
import json
import os
from datetime import datetime

# Test data matching the violation images we created - note exact domain names and timestamps
test_detections = [
    "[2025-07-14 07:15:00] [Manufacturing] NO-hardhat 0.92 (235, 0, 507, 125)",
    "[2025-07-14 07:15:00] [Construction] NO-Safety Vest 0.88 (232, 17, 485, 154)",
    "[2025-07-14 07:15:00] [Healthcare] NO-Mask 0.91 (219, 28, 480, 144)",
    "[2025-07-14 07:15:00] [Oil & Gas] NO-hardhat 0.87 (200, 50, 400, 200)",
    "[2025-07-14 07:45:00] [Manufacturing] NO-hardhat 0.94 (235, 0, 507, 125)",
    "[2025-07-14 07:45:00] [Construction] NO-Safety Vest 0.82 (232, 17, 485, 154)",
    "[2025-07-14 07:45:00] [Healthcare] NO-Mask 0.89 (219, 28, 480, 144)",
    "[2025-07-14 07:45:00] [Oil & Gas] NO-hardhat 0.93 (200, 50, 400, 200)",
    "[2025-07-14 08:30:00] [Manufacturing] NO-hardhat 0.86 (235, 0, 507, 125)",
    "[2025-07-14 08:30:00] [Construction] NO-Safety Vest 0.95 (232, 17, 485, 154)",
    "[2025-07-14 08:30:00] [Healthcare] NO-Mask 0.83 (219, 28, 480, 144)",
    "[2025-07-14 08:30:00] [Oil & Gas] NO-hardhat 0.90 (200, 50, 400, 200)"
]

def create_test_detection_file():
    """Create a test detection results file with sample confidence values."""
    print("📝 Creating test detection_results.txt with sample confidence values...")
    
    # Backup existing file if it exists
    if os.path.exists("detection_results.txt"):
        backup_name = f"detection_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.rename("detection_results.txt", backup_name)
        print(f"   Backed up existing file to: {backup_name}")
    
    # Write test data
    with open("detection_results.txt", "w") as f:
        for detection in test_detections:
            f.write(detection + "\n")
        f.write("\n")  # Add separator line
    
    print(f"   Created detection_results.txt with {len(test_detections)} test detections")

def test_confidence_extraction():
    """Test the violation images API to see if it extracts real confidence values."""
    print("\n🧪 Testing Confidence Extraction from Detection Results")
    print("=" * 60)
    
    try:
        # Test with time range that should match our test data
        response = requests.get(
            "http://localhost:5000/api/violation_images",
            params={
                'date': '2025-07-14',
                'time_from': '07:00',
                'time_to': '08:00'
            }
        )
        
        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        violations = response.json()
        print(f"📊 Found {len(violations)} violations in time range 07:00-08:00")
        
        if not violations:
            print("⚠️ No violations found - make sure violation images exist for the test time range")
            return False
        
        # Check confidence values
        confidence_found = False
        for violation in violations[:5]:  # Check first 5
            confidence = violation.get('confidence', 0)
            filename = violation.get('filename', 'unknown')
            violation_type = violation.get('violation_type', 'unknown')
            
            print(f"\n📸 {filename}")
            print(f"   Type: {violation_type}")
            print(f"   Confidence: {confidence}")
            
            # Check if confidence is not the default 0.85
            if confidence != 0.85:
                print(f"   ✅ Real confidence extracted: {confidence}")
                confidence_found = True
            else:
                print(f"   ⚠️ Using default confidence: {confidence}")
        
        if confidence_found:
            print(f"\n🎉 SUCCESS: Real confidence values are being extracted!")
        else:
            print(f"\n⚠️ All violations show default confidence (0.85)")
            print(f"   This might mean:")
            print(f"   - Detection file format doesn't match")
            print(f"   - Timestamp matching is not working")
            print(f"   - Domain name matching is not working")
        
        return confidence_found
        
    except Exception as e:
        print(f"❌ Error testing confidence extraction: {e}")
        return False

def show_detection_file_sample():
    """Show sample lines from the detection results file."""
    print("\n📄 Sample Detection Results File Content:")
    print("-" * 50)
    
    if os.path.exists("detection_results.txt"):
        with open("detection_results.txt", "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10], 1):
                line = line.strip()
                if line:
                    print(f"   {i:2d}: {line}")
    else:
        print("   detection_results.txt not found")

def main():
    print("CONFIDENCE EXTRACTION TEST")
    print("=" * 80)
    print("This test verifies that real confidence values are extracted from detection_results.txt")
    print("=" * 80)
    
    # Check if Flask server is running
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Flask server is running")
    except:
        print("❌ Flask server is not running. Please start it first.")
        print("   Command: python flaskapp.py 5000")
        return 1
    
    # Create test detection data
    create_test_detection_file()
    
    # Show sample detection data
    show_detection_file_sample()
    
    # Test confidence extraction
    success = test_confidence_extraction()
    
    print("\n" + "=" * 80)
    print("CONFIDENCE EXTRACTION TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print("✅ Confidence extraction is working correctly!")
        print("   Real confidence values from YOLO detections are being used.")
    else:
        print("⚠️ Confidence extraction needs debugging.")
        print("   Check the Flask app logs for detailed debug information.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
