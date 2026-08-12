"""
Internationalization (i18n) module

Uses Python's standard-library gettext under the hood.
All public API symbols are exposed at module level so callers can just:

    from battery_analysis.i18n import _, ngettext, pgettext
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from battery_analysis.i18n.translator import SimplePOTranslator

logger = logging.getLogger(__name__)

# Determine locale directory
if hasattr(sys, "_MEIPASS"):
    LOCALEDIR = Path(sys._MEIPASS) / "locale"
else:
    LOCALEDIR = Path(__file__).parent.parent.parent.parent / "locale"

logger.info("Using locale directory: %s", LOCALEDIR)

# Global state
_current_locale: str = "en"
_po_translator = SimplePOTranslator()


# ── Internal ──────────────────────────────────────────────────────


def _load_locale(locale_code: str) -> bool:
    """Load translations for *locale_code* into the global translator."""
    global _current_locale
    if _po_translator.load_locale(locale_code, LOCALEDIR):
        _current_locale = locale_code
        logger.info("Locale set to: %s", locale_code)
        return True
    return False


# ── Public API (stable contract for all callers) ──────────────────


def _(text: str, context: Optional[str] = None) -> str:
    """Translate *text*; return *text* itself if no translation exists."""
    try:
        if context:
            return _po_translator.pgettext(context, text)
        return _po_translator.gettext(text)
    except (AttributeError, KeyError) as exc:
        logger.warning("Translation error for '%s': %s", text, exc)
        return text


def pgettext(context: str, text: str) -> str:
    """Context-aware translation."""
    return _(text, context)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Plural translation (singular if n == 1, else plural)."""
    try:
        return _po_translator.ngettext(singular, plural, n)
    except (AttributeError, KeyError) as exc:
        logger.warning("Translation error for '%s'/'%s': %s", singular, plural, exc)
        return singular if n == 1 else plural


# ── Locale management ─────────────────────────────────────────────


def get_available_locales():
    from battery_analysis.i18n.locale_utils import (
        get_available_locales as _get_available,
    )

    return _get_available(LOCALEDIR)


def set_locale(locale_code: str) -> bool:
    """Switch to *locale_code* (must have a .po file under LOCALEDIR)."""
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
    except (OSError, ValueError, ImportError) as exc:
        logger.error("Failed to set locale '%s': %s", valid_locale, exc)
        import traceback

        traceback.print_exc()
        return False


def get_current_locale() -> str:
    """Return the currently active locale code."""
    return _current_locale


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
    return "en"


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


# Auto-initialize on import
initialize_default_locale()
logger.info("i18n module initialized with locale: %s", _current_locale)
