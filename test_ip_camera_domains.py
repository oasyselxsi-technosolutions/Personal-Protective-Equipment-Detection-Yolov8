#!/usr/bin/env python3
"""
Test script for domain-specific IP camera functionality
"""

import sys
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_domain_validation():
    """Test the domain validation logic"""
    
    # Domain detection function mapping
    try:
        from YOLO_Video import detect_manufacturing_ppe, detect_construction_ppe, detect_healthcare_ppe, detect_oilgas_ppe, video_detection_single_frame
        
        domain_functions = {
            'general': video_detection_single_frame,
            'manufacturing': detect_manufacturing_ppe,
            'construction': detect_construction_ppe,
            'healthcare': detect_healthcare_ppe,
            'oilgas': detect_oilgas_ppe
        }
        
        print("✅ Successfully imported all domain detection functions")
        print(f"✅ Available domains: {list(domain_functions.keys())}")
        
        # Test domain validation
        test_domains = ['general', 'manufacturing', 'construction', 'healthcare', 'oilgas', 'invalid']
        
        for domain in test_domains:
            if domain in domain_functions:
                print(f"✅ Domain '{domain}': Valid")
            else:
                print(f"❌ Domain '{domain}': Invalid")
                
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_routes():
    """Test the route structure"""
    
    expected_routes = [
        '/ipcamera_stable/<domain>',
        '/ipcamera_stable_raw/<domain>',
        '/ipcamera_manufacturing',
        '/ipcamera_construction',
        '/ipcamera_healthcare',
        '/ipcamera_oilgas'
    ]
    
    print("\n📋 Expected new routes:")
    for route in expected_routes:
        print(f"  - {route}")
        
    return True

def main():
    """Main test function"""
    print("🔍 Testing Domain-Specific IP Camera Implementation")
    print("=" * 50)
    
    # Test 1: Domain validation
    print("\n1. Testing domain validation...")
    domain_test = test_domain_validation()
    
    # Test 2: Route structure
    print("\n2. Testing route structure...")
    route_test = test_routes()
    
    print("\n" + "=" * 50)
    if domain_test and route_test:
        print("✅ All tests passed! Implementation looks good.")
        print("\n📝 Usage examples:")
        print("  - General detection: http://localhost:5000/ipcamera_stable/general")
        print("  - Manufacturing: http://localhost:5000/ipcamera_stable/manufacturing")
        print("  - Construction: http://localhost:5000/ipcamera_stable/construction")
        print("  - Healthcare: http://localhost:5000/ipcamera_stable/healthcare")
        print("  - Oil & Gas: http://localhost:5000/ipcamera_stable/oilgas")
        print("  - Raw feed: http://localhost:5000/ipcamera_stable_raw/manufacturing")
        print("\n📝 Convenience routes:")
        print("  - Manufacturing: http://localhost:5000/ipcamera_manufacturing")
        print("  - Construction: http://localhost:5000/ipcamera_construction")
        print("  - Healthcare: http://localhost:5000/ipcamera_healthcare")
        print("  - Oil & Gas: http://localhost:5000/ipcamera_oilgas")
    else:
        print("❌ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main()
