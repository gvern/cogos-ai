#!/usr/bin/env python3
"""
Script to check and fix Lottie animation files
"""
import os
import json
import shutil
from pathlib import Path

# Default animation to use if the original can't be fixed
DEFAULT_ANIMATION = {
    "v": "5.5.7",
    "fr": 30,
    "ip": 0,
    "op": 60,
    "w": 400,
    "h": 400,
    "nm": "CogOS Brain",
    "ddd": 0,
    "assets": [],
    "layers": [
        {
            "ddd": 0,
            "ind": 1,
            "ty": 4,
            "nm": "Brain",
            "sr": 1,
            "ks": {
                "o": { "a": 0, "k": 100 },
                "r": { 
                    "a": 1, 
                    "k": [
                        { "t": 0, "s": [0], "h": 0 },
                        { "t": 30, "s": [180], "h": 0 },
                        { "t": 60, "s": [360], "h": 0 }
                    ]
                },
                "p": { "a": 0, "k": [200, 200, 0] },
                "a": { "a": 0, "k": [0, 0, 0] },
                "s": { "a": 0, "k": [100, 100, 100] }
            },
            "shapes": [
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "el",
                            "p": { "a": 0, "k": [0, 0] },
                            "s": { "a": 0, "k": [150, 150] }
                        },
                        {
                            "ty": "st",
                            "c": { "a": 0, "k": [0.4, 0.8, 0.9, 1] },
                            "o": { "a": 0, "k": 100 },
                            "w": { "a": 0, "k": 8 }
                        },
                        {
                            "ty": "fl",
                            "c": { "a": 0, "k": [0.2, 0.4, 0.6, 0.3] },
                            "o": { "a": 0, "k": 30 }
                        }
                    ],
                    "nm": "Brain Circle"
                }
            ]
        }
    ]
}

def fix_lottie_file():
    # Paths
    input_file = Path("assets/cogos_lottie.lottie")
    backup_file = Path("assets/cogos_lottie.lottie.bak")
    fixed_file = Path("assets/cogos_lottie.lottie")
    fallback_file = Path("assets/Cogos_lottie.json")
    
    # Create assets directory if it doesn't exist
    os.makedirs("assets", exist_ok=True)
    
    # Make sure we have a fallback file
    if not fallback_file.exists():
        with open(fallback_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_ANIMATION, f, indent=2)
        print(f"Created fallback animation file: {fallback_file}")
    
    try:
        # If original file exists, attempt to fix it
        if input_file.exists():
            # Create backup if it doesn't exist
            if not backup_file.exists():
                shutil.copy2(input_file, backup_file)
                print(f"Created backup of original file: {backup_file}")
            
            # Try to read the file as binary
            try:
                with open(input_file, "rb") as f:
                    data = f.read()
                
                # Try different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8']:
                    try:
                        content = data.decode(encoding)
                        # If we can parse it as JSON, write it back as UTF-8
                        json_data = json.loads(content)
                        with open(fixed_file, "w", encoding="utf-8") as f:
                            json.dump(json_data, f, indent=2)
                        print(f"✅ Fixed animation file using {encoding} encoding")
                        return True
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                
                # None of the encodings worked, use the default animation
                print("❌ Could not decode the original file with any known encoding")
            except Exception as e:
                print(f"❌ Error reading the original file: {e}")
        
        # Use the default animation if all else fails
        print("⚠️ Using default animation")
        with open(fixed_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_ANIMATION, f, indent=2)
        return True
            
    except Exception as e:
        print(f"❌ Error fixing Lottie file: {e}")
        return False

if __name__ == "__main__":
    success = fix_lottie_file()
    if success:
        print("✅ Lottie animation file has been fixed or replaced")
    else:
        print("❌ Failed to fix Lottie animation file")