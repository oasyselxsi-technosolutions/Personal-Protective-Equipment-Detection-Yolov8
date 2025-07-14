#!/usr/bin/env python3
"""
Direct test of confidence extraction function using the same logic as Flask app
"""
import re
import os

DETECTION_RESULTS_FILE = "detection_results.txt"

def extract_confidence_from_detection_file(target_domain, target_timestamp):
    """
    Exact copy of the Flask function to test directly
    """
    try:
        if not os.path.exists(DETECTION_RESULTS_FILE):
            print(f"[DEBUG] Detection results file not found: {DETECTION_RESULTS_FILE}")
            return 0.85
        
        print(f"[DEBUG] Searching for confidence: domain='{target_domain}', timestamp='{target_timestamp}'")
        
        with open(DETECTION_RESULTS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                print(f"[DEBUG] Processing line: {line}")
                    
                # Parse line format: [2025-07-13 21:47:03] [Manufacturing] NO-hardhat 0.99 (x1, y1, x2, y2)
                m = re.match(r"\[(.*?)\] \[(.*?)\] (.+?) ([\d\.]+) \((.*?)\)", line)
                if m:
                    time_str, domain, vtype, conf_str, bbox = m.groups()
                    confidence = float(conf_str)
                    
                    print(f"[DEBUG] Parsed: time='{time_str}', domain='{domain}', type='{vtype}', conf={confidence}")
                    
                    # Check if this matches our target violation
                    if domain == target_domain and time_str == target_timestamp:
                        print(f"[DEBUG] Found matching confidence: {confidence} for {domain} at {time_str}")
                        return confidence
                    else:
                        if domain != target_domain:
                            print(f"[DEBUG] Domain mismatch: '{domain}' != '{target_domain}'")
                        if time_str != target_timestamp:
                            print(f"[DEBUG] Timestamp mismatch: '{time_str}' != '{target_timestamp}'")
                else:
                    print(f"[DEBUG] Line didn't match regex: {line}")
        
        print(f"[DEBUG] No matching confidence found for {target_domain} at {target_timestamp}")
        return 0.85  # Default confidence if not found
        
    except Exception as e:
        print(f"[ERROR] Error extracting confidence: {e}")
        return 0.85  # Default confidence on error

def main():
    print("🔍 Testing Confidence Extraction Function Directly")
    print("=" * 60)
    
    # Test cases based on what we know is in the detection file
    test_cases = [
        ("Manufacturing", "2025-07-14 07:45:00"),
        ("Construction", "2025-07-14 07:45:00"),
        ("Healthcare", "2025-07-14 07:45:00"),
        ("Oil & Gas", "2025-07-14 07:45:00"),
    ]
    
    for domain, timestamp in test_cases:
        print(f"\n🧪 Testing: domain='{domain}', timestamp='{timestamp}'")
        confidence = extract_confidence_from_detection_file(domain, timestamp)
        print(f"   Result: {confidence}")
        
        if confidence != 0.85:
            print(f"   ✅ Found real confidence: {confidence}")
        else:
            print(f"   ⚠️  Using default confidence: {confidence}")

if __name__ == "__main__":
    main()
