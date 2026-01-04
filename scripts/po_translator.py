#!/usr/bin/env python3
"""
Simple PO file-based translator
Directly uses .po files without compilation to .mo
"""

import sys
import os
import re
from pathlib import Path
import logging
import locale

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTranslator:
    """Simple translator that uses .po files directly"""
    
    def __init__(self):
        self.translations = {}
        self.current_locale = 'en'
    
    def parse_po_file(self, po_file_path):
        """Parse a .po file and extract translations"""
        translations = {}
        
        try:
            with open(po_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based parsing
            msgid_pattern = r'msgid\s+"([^"]*)"'
            msgstr_pattern = r'msgstr\s+"([^"]*)"'
            
            msgid_matches = list(re.finditer(msgid_pattern, content))
            msgstr_matches = list(re.finditer(msgstr_pattern, content))
            
            for i in range(min(len(msgid_matches), len(msgstr_matches))):
                msgid = msgid_matches[i].group(1)
                msgstr = msgstr_matches[i].group(1)
                
                # Skip empty msgid (header)
                if not msgid.strip():
                    continue
                
                translations[msgid] = msgstr
            
            logger.info("Parsed %s translations from %s", len(translations), po_file_path)
            return translations
            
        except Exception as e:
            logger.error("Error parsing %s: %s", po_file_path, e)
            return {}
    
    def load_locale(self, locale_code):
        """Load translations for a specific locale"""
        locale_dir = Path(__file__).parent.parent / "locale"
        po_file = locale_dir / locale_code / "LC_MESSAGES" / "messages.po"
        
        if not po_file.exists():
            logger.warning("Translation file not found: %s", po_file)
            return False
        
        self.translations = self.parse_po_file(po_file)
        self.current_locale = locale_code
        
        logger.info("Loaded %s translations for %s", len(self.translations), locale_code)
        return True
    
    def _(self, text, context=None):
        """Get translation for text"""
        if context:
            # Handle context-aware translations if needed
            key = f"{context}:{text}"
        else:
            key = text
        
        return self.translations.get(key, text)
    
    def set_locale(self, locale_code):
        """Set the current locale"""
        if self.load_locale(locale_code):
            logger.info("Successfully set locale to: %s", locale_code)
            return True
        else:
            logger.error("Failed to set locale to: %s", locale_code)
            return False
    
    def get_available_locales(self):
        """Get list of available locales"""
        locale_dir = Path(__file__).parent.parent / "locale"
        locales = []
        
        for locale_subdir in locale_dir.iterdir():
            if locale_subdir.is_dir():
                po_file = locale_subdir / "LC_MESSAGES" / "messages.po"
                if po_file.exists():
                    locales.append(locale_subdir.name)
        
        return locales
    
    def get_current_locale(self):
        """Get current locale"""
        return self.current_locale


# Global translator instance
_translator = SimpleTranslator()

def _(text, context=None):
    """Global translation function"""
    return _translator._(text, context)

def set_locale(locale_code):
    """Set the current locale"""
    return _translator.set_locale(locale_code)

def get_available_locales():
    """Get available locales"""
    return _translator.get_available_locales()

def get_current_locale():
    """Get current locale"""
    return _translator.get_current_locale()

def detect_system_locale():
    """Detect system locale"""
    try:
        result = locale.getdefaultlocale()
        if result and result[0]:
            lang_code = result[0].split('_')[0]
            return lang_code
    except:
        pass
    return 'en'

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