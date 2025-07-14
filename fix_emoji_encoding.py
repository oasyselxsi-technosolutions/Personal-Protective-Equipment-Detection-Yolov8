#!/usr/bin/env python3
"""
Script to replace emoji characters in flaskapp.py with ASCII-safe alternatives
"""
import re

def fix_emoji_encoding():
    """Replace problematic emoji characters with ASCII-safe alternatives"""
    
    try:
        # Read the file
        with open('flaskapp.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Define replacements for emoji characters
        replacements = [
            ('🎯 [DOMAIN-', '[DOMAIN-'),
            ('🎬 [FRAME-GEN-', '[FRAME-GEN-'),
            ('🚀 [STARTUP]', '[STARTUP]'),
            ('📝 Logs', '[INFO] Logs'),
            ('✓ Successfully', '[OK] Successfully'),
            ('✗ Connected', '[WARN] Connected'),
            ('✗ Failed', '[ERROR] Failed'),
            ('🔥 [ERROR]', '[ERROR]'),
            ('🔧 [CONFIG]', '[CONFIG]'),
            ('📊 [STATS]', '[STATS]'),
            ('⚠️ [WARNING]', '[WARNING]'),
            ('❌ [ERROR]', '[ERROR]'),
            ('✅ [SUCCESS]', '[SUCCESS]'),
            ('🎥 [CAMERA]', '[CAMERA]'),
            ('🔌 [CONNECTION]', '[CONNECTION]'),
            ('🎬 [RECORDING]', '[RECORDING]'),
            ('📸 [CAPTURE]', '[CAPTURE]'),
            ('💾 [SAVE]', '[SAVE]'),
            ('🏥 [HEALTHCARE]', '[HEALTHCARE]'),
            ('🏭 [MANUFACTURING]', '[MANUFACTURING]'),
            ('🏗️ [CONSTRUCTION]', '[CONSTRUCTION]'),
            ('⛽ [OILGAS]', '[OILGAS]'),
        ]
        
        # Apply replacements
        original_len = len(content)
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Write back to file
        with open('flaskapp.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Successfully processed flaskapp.py")
        print(f"  Original size: {original_len} characters")
        print(f"  Final size: {len(content)} characters")
        print(f"  Applied {len(replacements)} replacement patterns")
        
        return True
        
    except Exception as e:
        print(f"✗ Error processing file: {e}")
        return False

if __name__ == "__main__":
    fix_emoji_encoding()
