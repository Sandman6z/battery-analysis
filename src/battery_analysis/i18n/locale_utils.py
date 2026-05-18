"""Locale utility functions"""

import locale
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_available_locales(localedir: Path) -> List[str]:
    """Get list of available locales with translation files."""
    available = []
    if not localedir.exists():
        logger.warning("Locale directory not found: %s", localedir)
        return available
    for locale_path in localedir.iterdir():
        if locale_path.is_dir():
            po_file = locale_path / "LC_MESSAGES" / "messages.po"
            if po_file.exists():
                available.append(locale_path.name)
    return sorted(available)


def detect_system_locale() -> Optional[str]:
    """Detect the system locale. Returns locale code or None."""
    try:
        try:
            system_locale = locale.getlocale()[0]
        except (AttributeError, TypeError):
            locale_result = locale.getdefaultlocale()
            if isinstance(locale_result, tuple):
                system_locale = locale_result[0] if len(locale_result) >= 1 else None
            else:
                system_locale = locale_result if locale_result else None
    except (ValueError, OSError, TypeError, AttributeError):
        system_locale = None

    logger.debug("Detected system locale: %s", system_locale)
    if system_locale:
        return str(system_locale)
    return None


def resolve_locale_code(locale_code: str, available_locales: List[str]) -> Optional[str]:
    """Resolve a locale code or display name to an available locale code."""
    if locale_code in available_locales:
        return locale_code

    display_name_map = {
        "English": "en", "中文(简体)": "zh_CN", "Chinese (Simplified)": "zh_CN",
        "中文(繁體)": "zh_TW", "Chinese (Traditional)": "zh_TW",
        "日本語": "ja", "Japanese": "ja",
        "한국어": "ko", "Korean": "ko",
        "Français": "fr", "French": "fr",
        "Deutsch": "de", "German": "de",
        "Español": "es", "Spanish": "es",
        "Italiano": "it", "Italian": "it",
        "Português": "pt", "Portuguese": "pt",
        "Русский": "ru", "Russian": "ru",
        "العربية": "ar", "Arabic": "ar",
        "हिन्दी": "hi", "Hindi": "hi",
    }

    mapped = display_name_map.get(locale_code)
    if mapped and mapped in available_locales:
        return mapped
    return None


def system_locale_to_code(system_locale: str, available_locales: List[str]) -> Optional[str]:
    """Convert system locale string (e.g. 'zh_CN') to best matching available locale."""
    lang_code = system_locale.split('_')[0]

    # Special case for Chinese variants
    if lang_code == 'zh':
        if 'TW' in system_locale or 'HK' in system_locale:
            return 'zh_TW' if 'zh_TW' in available_locales else 'zh_CN'
        return 'zh_CN' if 'zh_CN' in available_locales else 'zh_TW'

    if system_locale in available_locales:
        return system_locale
    if lang_code in available_locales:
        return lang_code
    for loc in available_locales:
        if loc.startswith(lang_code):
            return loc
    return None
