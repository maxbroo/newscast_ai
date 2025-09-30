#!/usr/bin/env python3
"""
Test script for the fixed episode generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main import generate_new_enhanced_episode

def test_generation():
    print("🚀 Testing fixed episode generation...")
    
    # Test categories
    categories = {
        'politics': ['neutral'],
        'scope': ['global'],  
        'topics': ['technology', 'business']
    }
    
    try:
        result = generate_new_enhanced_episode(categories, target_duration=15)  # Shorter test
        if result:
            print(f"✅ Episode generated successfully: {result}")
            return True
        else:
            print("❌ Episode generation failed")
            return False
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

if __name__ == "__main__":
    success = test_generation()
    sys.exit(0 if success else 1)
