#!/usr/bin/env python3
"""
Create violation images with specific times for testing time range filtering
"""
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

def create_time_specific_violations():
    """Create violation images with specific times to test time filtering"""
    
    print("🕐 Creating time-specific violation images for testing...")
    
    base_dir = "static/violations"
    os.makedirs(base_dir, exist_ok=True)
    
    # Create violations at specific times throughout the day
    test_times = [
        ("07", "15", "00"),  # 07:15:00
        ("07", "30", "15"),  # 07:30:15
        ("07", "45", "30"),  # 07:45:30
        ("08", "00", "00"),  # 08:00:00
        ("14", "30", "00"),  # 14:30:00 (current time area)
        ("15", "00", "00"),  # 15:00:00
        ("18", "45", "00"),  # 18:45:00
    ]
    
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    
    for i, (hour, minute, second) in enumerate(test_times):
        domain = ["healthcare", "construction", "manufacturing", "oilgas"][i % 4]
        domain_dir = os.path.join(base_dir, domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        time_str = f"{hour}{minute}{second}"
        microseconds = f"{i * 111111:06d}"
        
        filename = f"violation_{domain}_{date_str}_{time_str}_{microseconds}.jpg"
        filepath = os.path.join(domain_dir, filename)
        
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color=(50 + i * 30, 100, 50))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((10, 10), f"PPE Violation - Time Test", fill=(255, 255, 255), font=font)
        draw.text((10, 40), f"Domain: {domain.upper()}", fill=(255, 255, 255), font=font)
        draw.text((10, 70), f"Time: {hour}:{minute}:{second}", fill=(255, 255, 255), font=font)
        draw.text((10, 100), f"Test #{i+1}", fill=(255, 255, 255), font=font)
        
        # Different colored boxes for different times
        color = (255, 0, 0) if hour.startswith('0') else (0, 255, 0)
        draw.rectangle([200, 200, 400, 350], outline=color, width=3)
        draw.text((210, 210), "Time Test", fill=color, font=font)
        
        img.save(filepath, 'JPEG')
        print(f"   Created: {filename} (Time: {hour}:{minute}:{second})")
    
    print(f"✅ Time-specific violation images created")
    
    # Show what we should find with different time ranges
    print(f"\n📊 Expected results for time range tests:")
    print(f"   07:00 - 08:00: Should find 4 violations")
    print(f"   07:00 - 07:30: Should find 2 violations") 
    print(f"   14:00 - 16:00: Should find 2 violations")
    print(f"   All day: Should find 7 new violations + existing ones")

if __name__ == "__main__":
    create_time_specific_violations()
