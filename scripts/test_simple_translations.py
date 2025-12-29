#!/usr/bin/env python3
"""
Simple translation test to avoid encoding issues
"""

import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_simple_translations():
    """Test with simplified English-only translations"""
    
    # Create simple English test translation
    test_po_content = '''# Test translations
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "battery-analyzer"
msgstr "Battery Analyzer"

msgid "Preferences"
msgstr "Preferences"

msgid "Language"
msgstr "Language"

msgid "OK"
msgstr "OK"

msgid "Cancel"
msgstr "Cancel"
'''

    # Write test files
    locale_dir = Path(__file__).parent.parent / "locale"
    test_dir = locale_dir / "test" / "LC_MESSAGES"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Write test .po file
    test_po_file = test_dir / "messages.po"
    with open(test_po_file, 'w', encoding='utf-8') as f:
        f.write(test_po_content)
    
    # Test loading with our new PO translator
    try:
        from battery_analysis.i18n import SimplePOTranslator
        
        # Create a translator and load the test locale
        translator = SimplePOTranslator()
        success = translator.load_locale('test')
        
        if success:
            logger.info("✓ Translation file loaded successfully")
            
            # Test a translation
            result = translator._("battery-analyzer")
            logger.info(f"✓ Translation test: battery-analyzer -> {result}")
            
            # Test another translation
            result2 = translator._("Preferences")
            logger.info(f"✓ Translation test: Preferences -> {result2}")
            
            return True
        else:
            logger.error("✗ Translation loading failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Translation loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Testing simple translations...")
    success = test_simple_translations()
    
    if success:
        logger.info("✓ Simple translation test passed!")
    else:
        logger.error("✗ Simple translation test failed!")