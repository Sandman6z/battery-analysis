#!/usr/bin/env python3
"""
Internationalization Test Script

This script tests the i18n functionality of the Battery Analysis application.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from battery_analysis.i18n import _, set_locale, get_available_locales


def test_translations():
    """Test translation functionality"""
    print("Testing Internationalization Framework")
    print("=" * 40)
    
    # Test available locales
    locales = get_available_locales()
    print(f"Available locales: {locales}")
    
    # Test translations
    test_strings = [
        "battery-analyzer",
        "Preferences", 
        "Language",
        "OK",
        "Cancel",
        "File",
        "Edit",
        "Help",
        "About"
    ]
    
    print("\nTesting English translations:")
    set_locale("en")
    for string in test_strings:
        translated = _(string)
        print(f"  {string} -> {translated}")
    
    print("\nTesting Chinese translations:")
    set_locale("zh_CN")
    for string in test_strings:
        translated = _(string)
        print(f"  {string} -> {translated}")
    
    print("\ni18n test completed successfully!")


if __name__ == "__main__":
    test_translations()
