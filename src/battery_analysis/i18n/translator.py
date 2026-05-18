"""Simple .po file translator"""

import re
import logging
from pathlib import Path
from typing import Dict, Optional


class SimplePOTranslator:
    """Simple translator that uses .po files directly"""

    def __init__(self):
        self.translations: Dict[str, str] = {}
        self.current_locale = 'en'

    def parse_po_file(self, po_file_path: Path) -> Dict[str, str]:
        """Parse a .po file and extract translations"""
        translations = {}
        try:
            with open(po_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            msgid_pattern = r'msgid\s+"([^"]*)"'
            msgstr_pattern = r'msgstr\s+"([^"]*)"'

            msgid_matches = list(re.finditer(msgid_pattern, content))
            msgstr_matches = list(re.finditer(msgstr_pattern, content))

            for i in range(min(len(msgid_matches), len(msgstr_matches))):
                msgid = msgid_matches[i].group(1)
                msgstr = msgstr_matches[i].group(1)
                if not msgid.strip():
                    continue
                translations[msgid] = msgstr

            logging.getLogger(__name__).info(
                "Parsed %s translations from %s", len(translations), po_file_path)
            return translations
        except (IOError, UnicodeDecodeError, SyntaxError) as e:
            logging.getLogger(__name__).error("Error parsing %s: %s", po_file_path, e)
            return {}

    def load_locale(self, locale_code: str, localedir: Path) -> bool:
        """Load translations for a specific locale"""
        po_file = localedir / locale_code / "LC_MESSAGES" / "messages.po"
        if not po_file.exists():
            logging.getLogger(__name__).warning("Translation file not found: %s", po_file)
            return False
        self.translations = self.parse_po_file(po_file)
        self.current_locale = locale_code
        logging.getLogger(__name__).info(
            "Loaded %s translations for %s", len(self.translations), locale_code)
        return True

    def get(self, text: str, context: Optional[str] = None) -> str:
        """Get translation for text"""
        key = f"{context}:{text}" if context else text
        return self.translations.get(key, text)
