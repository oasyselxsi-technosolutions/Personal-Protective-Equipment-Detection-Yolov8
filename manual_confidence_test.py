#!/usr/bin/env python3
"""
Manual test of confidence extraction function
"""
import sys
import os
import re

# Add the current directory to the path to import from flaskapp
sys.path.append('.')

def manual_test_confidence_extraction():
    """Manually test the confidence extraction logic."""
    
    # Simulate the function logic directly
    DETECTION_RESULTS_FILE = "detection_results.txt"
    target_domain = "Construction"
    target_timestamp = "2025-07-14 07:45:00"
    
    print(f"🔍 Manual Confidence Extraction Test")
    print(f"   File: {DETECTION_RESULTS_FILE}")
    print(f"   Target Domain: '{target_domain}'")
    print(f"   Target Timestamp: '{target_timestamp}'")
    print("-" * 50)
    
    if not os.path.exists(DETECTION_RESULTS_FILE):
        print(f"❌ Detection results file not found: {DETECTION_RESULTS_FILE}")
        return 0.85
    
    with open(DETECTION_RESULTS_FILE, "r") as f:
        line_count = 0
        for line in f:
            line_count += 1
            line = line.strip()
            if not line:
                continue
                
            print(f"Line {line_count}: {line}")
            
            # Parse line format: [2025-07-13 21:47:03] [Manufacturing] NO-hardhat 0.99 (x1, y1, x2, y2)
            m = re.match(r"\[(.*?)\] \[(.*?)\] ([\w\-]+) ([\d\.]+) \((.*?)\)", line)
            if m:
                time_str, domain, vtype, conf_str, bbox = m.groups()
                print(f"   Parsed: time='{time_str}', domain='{domain}', vtype='{vtype}', conf='{conf_str}'")
                
                # Check if this matches our target violation
                if domain == target_domain and time_str == target_timestamp:
                    confidence = float(conf_str)
                    print(f"   ✅ MATCH FOUND! Confidence: {confidence}")
                    return confidence
                else:
                    if domain != target_domain:
                        print(f"   ❌ Domain mismatch: '{domain}' != '{target_domain}'")
                    if time_str != target_timestamp:
                        print(f"   ❌ Time mismatch: '{time_str}' != '{target_timestamp}'")
            else:
                print(f"   ❌ Line doesn't match expected format")
    
    print(f"   ❌ No matching confidence found")
    return 0.85

if __name__ == "__main__":
    confidence = manual_test_confidence_extraction()
    print(f"\n🎯 Final Result: {confidence}")
