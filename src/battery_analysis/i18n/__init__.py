"""
Internationalization (i18n) module
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from battery_analysis.i18n.translator import SimplePOTranslator

logger = logging.getLogger(__name__)

# Determine locale directory
if hasattr(sys, '_MEIPASS'):
    LOCALEDIR = Path(sys._MEIPASS) / "locale"
else:
    LOCALEDIR = Path(__file__).parent.parent.parent.parent / "locale"

logger.info("Using locale directory: %s", LOCALEDIR)

# Global state
_current_locale: str = "en"
_translations: Dict[str, Dict[str, str]] = {}
_po_translator = SimplePOTranslator()


def _load_locale(locale_code: str) -> bool:
    """Load translations for a locale into the global translator."""
    global _translations, _current_locale
    if _po_translator.load_locale(locale_code, LOCALEDIR):
        _translations[locale_code] = dict(_po_translator.translations)
        _current_locale = locale_code
        logger.info("Locale set to: %s", locale_code)
        return True
    return False


def get_available_locales():
    from battery_analysis.i18n.locale_utils import get_available_locales as _get_available
    return _get_available(LOCALEDIR)


def set_locale(locale_code: str) -> bool:
    """Set the current locale."""
    logger.info("Setting locale to: %s", locale_code)

    from battery_analysis.i18n.locale_utils import (
        get_available_locales as _get_available,
        resolve_locale_code,
    )

    available = _get_available(LOCALEDIR)
    valid_locale = resolve_locale_code(locale_code, available)
    if valid_locale is None:
        logger.warning("Locale '%s' not available", locale_code)
        return False

    try:
        return _load_locale(valid_locale)
    except (OSError, ValueError, ImportError) as e:
        logger.error("Failed to set locale '%s': %s", valid_locale, e)
        import traceback
        traceback.print_exc()
        return False


def _(text: str, context: Optional[str] = None) -> str:
    """Translate text."""
    try:
        return _po_translator.get(text, context)
    except (AttributeError, KeyError) as e:
        logging.warning("Translation error for '%s': %s", text, e)
        return text


def pgettext(context: str, text: str) -> str:
    """Context-aware translation."""
    return _(text, context)


def get_current_locale() -> str:
    """Get the current locale code."""
    return _current_locale


def ngettext(singular: str, plural: str, n: int) -> str:
    """Plural form translation (fallback to simple singular/plural)."""
    if _current_locale in _translations:
        try:
            return _translations[_current_locale].get(singular, singular if n == 1 else plural)
        except (AttributeError, KeyError) as e:
            logging.warning("Translation error for '%s/%s': %s", singular, plural, e)
    return singular if n == 1 else plural


def detect_system_locale() -> str:
    """Detect system locale, falling back to 'en'."""
    from battery_analysis.i18n.locale_utils import (
        detect_system_locale as _detect,
        system_locale_to_code,
        get_available_locales as _get_available,
    )
    sys_locale = _detect()
    if sys_locale:
        available = _get_available(LOCALEDIR)
        result = system_locale_to_code(sys_locale, available)
        if result:
            return result
    logger.info("Falling back to English locale")
    return 'en'


def initialize_default_locale() -> bool:
    """Initialize with system locale or fallback to English."""
    from battery_analysis.i18n.locale_utils import (
        detect_system_locale as _detect,
        get_available_locales as _get_available,
        system_locale_to_code,
    )

    sys_locale = _detect()
    if sys_locale:
        available = _get_available(LOCALEDIR)
        code = system_locale_to_code(sys_locale, available)
        if code and set_locale(code):
            return True
    return set_locale("en")


# Auto-initialize
initialize_default_locale()
logger.info("i18n module initialized with locale: %s", _current_locale)
