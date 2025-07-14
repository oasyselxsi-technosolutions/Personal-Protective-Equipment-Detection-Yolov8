#!/usr/bin/env python3
"""
Create sample violation images for testing the violations listing feature
"""
import os
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def create_sample_violation_images():
    """Create sample violation images with proper naming convention"""
    
    print("🧪 Creating sample violation images for testing...")
    
    # Create base violations directory
    base_dir = "static/violations"
    os.makedirs(base_dir, exist_ok=True)
    
    # Sample domains
    domains = ["healthcare", "construction", "manufacturing", "oilgas"]
    
    # Create sample images for today and yesterday
    today = datetime.now()
    
    for domain in domains:
        domain_dir = os.path.join(base_dir, domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        # Create 3-5 sample violation images per domain
        for i in range(3):
            # Generate timestamp for today
            timestamp_str = today.strftime("%Y%m%d_%H%M%S")
            microseconds = f"{i * 123456:06d}"
            
            filename = f"violation_{domain}_{timestamp_str}_{microseconds}.jpg"
            filepath = os.path.join(domain_dir, filename)
            
            # Create a simple test image
            img = Image.new('RGB', (640, 480), color=(100 + i * 50, 50, 50))
            draw = ImageDraw.Draw(img)
            
            # Add some text to make it look like a violation detection
            try:
                # Try to use default font, fall back to basic if not available
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((10, 10), f"PPE Violation Detected", fill=(255, 255, 255), font=font)
            draw.text((10, 40), f"Domain: {domain.upper()}", fill=(255, 255, 255), font=font)
            draw.text((10, 70), f"Time: {today.strftime('%H:%M:%S')}", fill=(255, 255, 255), font=font)
            draw.text((10, 100), f"Sample #{i+1}", fill=(255, 255, 255), font=font)
            
            # Draw a simple rectangle to simulate detection box
            draw.rectangle([200, 200, 400, 350], outline=(255, 0, 0), width=3)
            draw.text((210, 210), "Missing Helmet", fill=(255, 0, 0), font=font)
            
            img.save(filepath, 'JPEG')
            print(f"   Created: {filepath}")
    
    print(f"✅ Sample violation images created in {base_dir}")
    print(f"📁 Structure:")
    
    # Show the directory structure
    for domain in domains:
        domain_dir = os.path.join(base_dir, domain)
        if os.path.exists(domain_dir):
            files = os.listdir(domain_dir)
            print(f"   {domain}/: {len(files)} files")
            for file in files[:2]:  # Show first 2 files
                print(f"      - {file}")
            if len(files) > 2:
                print(f"      - ... and {len(files) - 2} more")

if __name__ == "__main__":
    create_sample_violation_images()
