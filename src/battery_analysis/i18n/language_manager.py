"""
Standard Language Manager for Battery Analysis application

This module provides a comprehensive language management system following
international standards and best practices for Python GUI applications.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication

from . import (
    _, ngettext, pgettext, set_locale, get_current_locale, 
    get_available_locales, detect_system_locale
)


class LanguageManager(QObject):
    """Language Manager following international standards"""
    
    # Signals for language changes
    language_changed = pyqtSignal(str)  # Emitted when language changes
    locale_changed = pyqtSignal(str)    # Emitted when locale changes
    
    # Supported locales with display names
    SUPPORTED_LOCALES = {
        "en": "English",
        "zh_CN": "中文(简体)",
        "zh_TW": "中文(繁體)",
        "ja": "日本語",
        "ko": "한국어",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "it": "Italiano",
        "pt": "Português",
        "ru": "Русский",
        "ar": "العربية",
        "hi": "हिन्दी"
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.settings = QSettings()
        
        # Connect to application instance
        self.app = QApplication.instance()
        
        # Initialize locale settings
        self._initialize_settings()
        
        # Connect signals
        self.language_changed.connect(self._on_language_changed)
        
        self.logger.info("Language Manager initialized")
    
    def _initialize_settings(self):
        """Initialize language settings from configuration"""
        # Get saved language preference or detect system locale
        saved_locale = self.settings.value("language/locale", "")
        
        if not saved_locale:
            # Detect system locale on first run
            saved_locale = detect_system_locale()
            self.settings.setValue("language/locale", saved_locale)
        
        # Set the detected/saved locale
        if self.set_locale(saved_locale):
            self.logger.info("Language Manager initialized with locale: %s", saved_locale)
        else:
            self.logger.warning("Failed to set locale to %s, falling back to English", saved_locale)
            self.set_locale("en")
    
    def get_available_locales(self) -> Dict[str, str]:
        """
        Get all available locales.
        
        Returns:
            Dictionary mapping locale codes to display names
        """
        return self.SUPPORTED_LOCALES
    
    def get_installed_locales(self) -> Dict[str, str]:
        """
        Get only locales that have translation files installed.
        
        Returns:
            Dictionary mapping locale codes to display names
        """
        installed = {}
        for locale_code, display_name in self.SUPPORTED_LOCALES.items():
            if self._has_translation_file(locale_code):
                installed[locale_code] = display_name
        
        return installed
    
    def _has_translation_file(self, locale_code: str) -> bool:
        """Check if translation file exists for locale"""
        locale_dir = Path(__file__).parent.parent.parent.parent / "locale" / locale_code / "LC_MESSAGES"
        mo_file = locale_dir / "messages.mo"
        return mo_file.exists()
    
    def get_current_locale(self) -> str:
        """
        Get current locale code.
        
        Returns:
            Current locale code
        """
        return get_current_locale()
    
    def set_locale(self, locale_code: str) -> bool:
        """
        Set the current locale and update translations.
        
        Args:
            locale_code: Locale code to set
            
        Returns:
            True if locale was set successfully
        """
        if locale_code not in self.SUPPORTED_LOCALES:
            self.logger.warning("Unsupported locale: %s", locale_code)
            return False
        
        if not self._has_translation_file(locale_code):
            self.logger.warning("No translation file for locale: %s", locale_code)
            return False
        
        # Set locale using standard gettext
        if set_locale(locale_code):
            self.settings.setValue("language/locale", locale_code)
            self.language_changed.emit(locale_code)
            self.locale_changed.emit(locale_code)
            self.logger.info("Locale set to: %s", locale_code)
            return True
        else:
            self.logger.error("Failed to set locale to: %s", locale_code)
            return False
    
    def get_text(self, text: str, context: Optional[str] = None) -> str:
        """
        Get translated text.
        
        Args:
            text: Text to translate
            context: Optional context for disambiguation
            
        Returns:
            Translated text
        """
        if context:
            return pgettext(context, text)
        else:
            # Use direct translation from gettext instead of global _ function
            return self._direct_translate(text)
    
    def _direct_translate(self, text: str) -> str:
        """
        Direct translation using the same mechanism as i18n module.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text
        """
        try:
            # Import the same SimplePOTranslator used in i18n module
            from . import _po_translator
            return _po_translator._(text)
        except (ImportError, AttributeError, KeyError) as e:
            self.logger.warning("Translation failed for '%s': %s", text, e)
            return text
    
    def get_plural_text(self, singular: str, plural: str, n: int) -> str:
        """
        Get translated plural text.
        
        Args:
            singular: Singular form
            plural: Plural form
            n: Number to determine form
            
        Returns:
            Translated text in appropriate form
        """
        return ngettext(singular, plural, n)
    
    def format_translation(self, template: str, **kwargs) -> str:
        """
        Format a translated string with placeholders.
        
        Args:
            template: Template string with {placeholders}
            **kwargs: Values to insert into placeholders
            
        Returns:
            Formatted translated string
        """
        translated = _(template)
        try:
            return translated.format(**kwargs)
        except (KeyError, ValueError) as e:
            self.logger.warning("Translation formatting error: %s", e)
            return translated
    
    def _on_language_changed(self, locale_code: str):
        """Handle language change signal"""
        self.logger.info("Language changed to: %s", locale_code)
        
        # Update UI language if needed
        self._update_ui_language(locale_code)
    
    def _update_ui_language(self, locale_code: str):
        """Update UI language elements"""
        try:
            # Trigger UI updates by emitting signals that widgets can connect to
            # This allows UI elements to refresh their translations
            
            # For Qt Designer UI files, they need to be recompiled with translations
            # or use dynamic translation updates
            
            pass  # Placeholder for UI-specific language updates
            
        except (AttributeError, TypeError) as e:
            self.logger.error("Failed to update UI language: %s", e)
    
    def reload_translations(self) -> bool:
        """
        Reload translations for current locale.
        
        Returns:
            True if reload successful
        """
        current_locale = self.get_current_locale()
        return self.set_locale(current_locale)
    
    def save_preferences(self):
        """Save current language preferences"""
        self.settings.sync()
        self.logger.debug("Language preferences saved")
    
    def load_preferences(self):
        """Load language preferences"""
        # This is called during initialization
        pass
    
    def reset_to_default(self):
        """Reset to system default language"""
        system_locale = detect_system_locale()
        if self.set_locale(system_locale):
            self.logger.info("Reset to system default: %s", system_locale)
        else:
            self.logger.warning("Failed to reset to system default")
    
    def get_locale_info(self, locale_code: str) -> Dict[str, Any]:
        """
        Get detailed information about a locale.
        
        Args:
            locale_code: Locale code
            
        Returns:
            Dictionary with locale information
        """
        if locale_code not in self.SUPPORTED_LOCALES:
            return {}
        
        return {
            "code": locale_code,
            "name": self.SUPPORTED_LOCALES[locale_code],
            "installed": self._has_translation_file(locale_code),
            "current": self.get_current_locale() == locale_code
        }
    
    # Alias methods for backward compatibility and ease of use
    def get_available_languages(self) -> Dict[str, str]:
        """Alias for get_available_locales()"""
        return self.get_available_locales()
    
    def get_installed_languages(self) -> Dict[str, str]:
        """Alias for get_installed_locales()"""
        return self.get_installed_locales()
    
    def get_current_language(self) -> str:
        """Alias for get_current_locale()"""
        return self.get_current_locale()
    
    def set_language(self, language_code: str) -> bool:
        """Alias for set_locale()"""
        return self.set_locale(language_code)
    
    def export_translations(self, locale_code: str, output_path: str) -> bool:
        """
        Export translations for a locale to JSON format.
        
        Args:
            locale_code: Locale to export
            output_path: Output file path
            
        Returns:
            True if export successful
        """
        try:
            import json
            
            # This would require parsing the .po file
            # For now, return False as this is a complex operation
            self.logger.warning("Translation export not implemented yet")
            return False
            
        except (ImportError, IOError, UnicodeError) as e:
            self.logger.error("Failed to export translations: %s", e)
            return False
    
    def validate_translations(self, locale_code: str) -> Dict[str, bool]:
        """
        Validate that translations exist for common UI elements.
        
        Args:
            locale_code: Locale to validate
            
        Returns:
            Dictionary mapping translation keys to existence status
        """
        common_keys = [
            "OK", "Cancel", "Apply", "Save", "Open", "Close",
            "File", "Edit", "Help", "About", "Preferences",
            "Language", "Error", "Warning", "Information"
        ]
        
        validation = {}
        old_locale = self.get_current_locale()
        
        try:
            # Temporarily switch to target locale for validation
            if self.set_locale(locale_code):
                for key in common_keys:
                    translated = _(key)
                    validation[key] = translated != key
                
                # Switch back
                self.set_locale(old_locale)
        
        except Exception as e:
            self.logger.error("Translation validation failed: %s", e)
            validation = {key: False for key in common_keys}
        
        return validation


# Global language manager instance
_language_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """
    Get the global language manager instance.
    
    Returns:
        Global LanguageManager instance
    """
    global _language_manager
    
    if _language_manager is None:
        _language_manager = LanguageManager()
    
    return _language_manager


