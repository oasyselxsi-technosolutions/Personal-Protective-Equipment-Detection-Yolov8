#!/usr/bin/env python3
"""
Create test violation images to verify the violations listing functionality
Uses the correct domain folder naming from YOLO_Video.py: domain_short = ''.join([c for c in domain_name if c.isalnum()])[:4]
"""
import os
import cv2
import numpy as np
from datetime import datetime, timedelta

def create_test_violation_images():
    """Create sample violation images for testing"""
    
    # Domain mappings based on YOLO_Video.py logic: domain_short = ''.join([c for c in domain_name if c.isalnum()])[:4]
    domains = {
        'Manufacturing': 'Manu',
        'Construction': 'Cons', 
        'Healthcare': 'Heal',
        'Oil & Gas': 'OilG'
    }
    
    base_dir = "static/violations"
    
    print("[DEBUG] Creating test violation images...")
    
    # Create base directory
    os.makedirs(base_dir, exist_ok=True)
    
    # Create sample times for different hours
    base_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    sample_times = [
        base_date.replace(hour=7, minute=15),   # 07:15
        base_date.replace(hour=7, minute=45),   # 07:45
        base_date.replace(hour=8, minute=30),   # 08:30
        base_date.replace(hour=9, minute=10),   # 09:10
        base_date.replace(hour=14, minute=20),  # 14:20
        base_date.replace(hour=16, minute=50),  # 16:50
    ]
    
    violation_types = ['NO-Mask', 'NO-Safety Vest', 'NO-hardhat']
    
    created_files = []
    
    for domain_name, domain_short in domains.items():
        # Create domain directory
        domain_dir = os.path.join(base_dir, domain_short)
        os.makedirs(domain_dir, exist_ok=True)
        
        print(f"[DEBUG] Creating violations for {domain_name} (folder: {domain_short})")
        
        # Create 2-3 violations per domain at different times
        for i, sample_time in enumerate(sample_times[:3]):  # Use first 3 times per domain
            violation_type = violation_types[i % len(violation_types)]
            
            # Format timestamp for filename: YYYYMMDD_HHMMSS_microseconds
            time_str = sample_time.strftime('%Y%m%d_%H%M%S_%f')
            
            # Create filename in format: violation_DomainName_YYYYMMDD_HHMMSS_microseconds.jpg
            filename = f"violation_{domain_name}_{time_str}.jpg"
            filepath = os.path.join(domain_dir, filename)
            
            # Create a simple test image (red rectangle with text)
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            img.fill(50)  # Dark gray background
            
            # Draw red violation indicator
            cv2.rectangle(img, (50, 50), (590, 100), (0, 0, 255), 3)
            
            # Add text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, f"{domain_name} Violation", (60, 80), font, 0.8, (255, 255, 255), 2)
            cv2.putText(img, f"Type: {violation_type}", (60, 150), font, 0.6, (255, 255, 255), 2)
            cv2.putText(img, f"Time: {sample_time.strftime('%Y-%m-%d %H:%M:%S')}", (60, 200), font, 0.5, (255, 255, 255), 1)
            cv2.putText(img, f"Confidence: 0.{85 + i*2}", (60, 250), font, 0.5, (255, 255, 255), 1)
            
            # Save the image
            cv2.imwrite(filepath, img)
            created_files.append({
                'domain': domain_name,
                'domain_short': domain_short,
                'filename': filename,
                'filepath': filepath,
                'timestamp': sample_time.isoformat(),
                'violation_type': violation_type
            })
            
            print(f"[DEBUG]   Created: {filename}")
    
    print(f"[DEBUG] Successfully created {len(created_files)} test violation images")
    print("[DEBUG] Summary:")
    for domain_name, domain_short in domains.items():
        domain_files = [f for f in created_files if f['domain'] == domain_name]
        print(f"[DEBUG]   {domain_name} ({domain_short}): {len(domain_files)} files")
    
    print(f"[DEBUG] Files created in: {os.path.abspath(base_dir)}")
    
    # Verify directory structure
    print("[DEBUG] Directory structure:")
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"[DEBUG] {indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"[DEBUG] {subindent}{file}")
    
    return created_files

if __name__ == "__main__":
    create_test_violation_images()
