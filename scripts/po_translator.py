#!/usr/bin/env python3
"""
Simple PO file-based translator
Directly uses .po files without compilation to .mo
"""

import sys
import os
from pathlib import Path
import logging

# Add src directory to path so we can import the main i18n module
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the main i18n module instead of duplicating code
from battery_analysis.i18n import (
    _ as main_translate,
    set_locale as main_set_locale,
    get_available_locales as main_get_available_locales,
    get_current_locale as main_get_current_locale,
    detect_system_locale as main_detect_system_locale
)

# Re-export the functions from the main module
def _(text, context=None):
    """Global translation function"""
    return main_translate(text, context)

def set_locale(locale_code):
    """Set the current locale"""
    return main_set_locale(locale_code)

def get_available_locales():
    """Get available locales"""
    return main_get_available_locales()

def get_current_locale():
    """Get current locale"""
    return main_get_current_locale()

def detect_system_locale():
    """Detect system locale"""
    return main_detect_system_locale()




def initialize_i18n():
    """Initialize internationalization"""
    # Detect system locale
    system_locale = detect_system_locale()
    available_locales = get_available_locales()
    
    # Use system locale if available, otherwise use 'en'
    if system_locale in available_locales:
        locale_code = system_locale
    else:
        locale_code = 'en'
    
    # Set locale
    if set_locale(locale_code):
        logger.info("i18n initialized with locale: %s", locale_code)
        return locale_code
    else:
        logger.warning("Failed to initialize i18n, using default")
        return 'en'


def main():
    """Test the simple translator"""
    print("Testing Simple PO-based Translator")
    print("=" * 40)
    
    # Initialize
    current_locale = initialize_i18n()
    print(f"Current locale: {current_locale}")
    
    # Test translations
    test_strings = [
        "battery-analyzer",
        "Preferences", 
        "Language",
        "OK",
        "Cancel"
    ]
    
    print("\nTesting current locale translations:")
    for text in test_strings:
        translated = _(text)
        print(f"  {text} -> {translated}")
    
    # Test locale switching
    available = get_available_locales()
    print(f"\nAvailable locales: {available}")
    
    for locale_code in available:
        print(f"\nTesting {locale_code}:")
        set_locale(locale_code)
        for text in test_strings[:3]:  # Test first 3 strings
            translated = _(text)
            print(f"  {text} -> {translated}")


if __name__ == "__main__":
    main()