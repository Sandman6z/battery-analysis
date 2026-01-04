#!/usr/bin/env python3
"""
Preferences Dialog Module

This module implements the preferences dialog for language and other application settings.
"""

import logging
from typing import Optional

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

from . import _, get_available_locales, set_locale, get_current_locale
from .language_manager import get_language_manager


class PreferencesDialog(QW.QDialog):
    """Preferences dialog for application settings"""
    
    # Signal emitted when preferences are applied
    preferences_applied = QC.pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the preferences dialog"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Get language manager
        self.language_manager = get_language_manager()
        
        # Set dialog properties
        self.setWindowTitle(_("preferences_title", "Preferences"))
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        # Initialize UI
        self._setup_ui()
        self._load_settings()
        
        self.logger.info("Preferences dialog initialized")
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Create main layout
        main_layout = QW.QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QW.QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create General tab
        self._create_general_tab()
        
        # Create Language tab
        self._create_language_tab()
        
        # Create buttons
        self._create_buttons(main_layout)
    
    def _create_general_tab(self):
        """Create the general preferences tab"""
        general_widget = QW.QWidget()
        general_layout = QW.QVBoxLayout(general_widget)
        
        # General settings group
        general_group = QW.QGroupBox(_("general_settings", "General Settings"))
        general_group_layout = QW.QVBoxLayout(general_group)
        
        # Auto-save option
        self.auto_save_checkbox = QW.QCheckBox(_("auto_save", "Auto-save settings"))
        self.auto_save_checkbox.setToolTip(_("auto_save_tooltip", "Automatically save settings when changes are made"))
        general_group_layout.addWidget(self.auto_save_checkbox)
        
        # Confirmation on exit
        self.confirm_exit_checkbox = QW.QCheckBox(_("confirm_exit", "Confirm before exiting"))
        self.confirm_exit_checkbox.setToolTip(_("confirm_exit_tooltip", "Show confirmation dialog when exiting the application"))
        general_group_layout.addWidget(self.confirm_exit_checkbox)
        
        general_layout.addWidget(general_group)
        
        # Display settings group
        display_group = QW.QGroupBox(_("display_settings", "Display Settings"))
        display_group_layout = QW.QVBoxLayout(display_group)
        
        # Theme selection
        theme_layout = QW.QHBoxLayout()
        theme_layout.addWidget(QW.QLabel(_("theme", "Theme:")))
        self.theme_combo = QW.QComboBox()
        self.theme_combo.addItems([
            _("theme_light", "Light"),
            _("theme_dark", "Dark"),
            _("theme_system", "System")
        ])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        display_group_layout.addLayout(theme_layout)
        
        # Font size
        font_layout = QW.QHBoxLayout()
        font_layout.addWidget(QW.QLabel(_("font_size", "Font Size:")))
        self.font_size_spinbox = QW.QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setSuffix(" pt")
        font_layout.addWidget(self.font_size_spinbox)
        font_layout.addStretch()
        display_group_layout.addLayout(font_layout)
        
        general_layout.addWidget(display_group)
        
        # Add stretch to push groups to top
        general_layout.addStretch()
        
        # Add tab
        self.tab_widget.addTab(general_widget, _("general", "General"))
    
    def _create_language_tab(self):
        """Create the language preferences tab"""
        language_widget = QW.QWidget()
        language_layout = QW.QVBoxLayout(language_widget)
        
        # Language selection group
        language_group = QW.QGroupBox(_("language_settings", "Language Settings"))
        language_group_layout = QW.QVBoxLayout(language_group)
        
        # Current language display
        current_lang_layout = QW.QHBoxLayout()
        current_lang_layout.addWidget(QW.QLabel(_("current_language", "Current Language:")))
        self.current_language_label = QW.QLabel()
        current_lang_layout.addWidget(self.current_language_label)
        current_lang_layout.addStretch()
        language_group_layout.addLayout(current_lang_layout)
        
        # Language selection
        lang_selection_layout = QW.QHBoxLayout()
        lang_selection_layout.addWidget(QW.QLabel(_("select_language", "Select Language:")))
        self.language_combo = QW.QComboBox()
        self._populate_language_combo()
        lang_selection_layout.addWidget(self.language_combo)
        lang_selection_layout.addStretch()
        language_group_layout.addLayout(lang_selection_layout)
        
        # Apply button
        apply_lang_button = QW.QPushButton(_("apply_language", "Apply Language"))
        apply_lang_button.clicked.connect(self._apply_language)
        language_group_layout.addWidget(apply_lang_button)
        
        language_layout.addWidget(language_group)
        
        # Translation status group
        status_group = QW.QGroupBox(_("translation_status", "Translation Status"))
        status_layout = QW.QVBoxLayout(status_group)
        
        # Status text
        self.status_text = QW.QLabel(_("translation_info", "Translation information will be displayed here."))
        self.status_text.setWordWrap(True)
        status_layout.addWidget(self.status_text)
        
        language_layout.addWidget(status_group)
        
        # Add stretch
        language_layout.addStretch()
        
        # Add tab
        self.tab_widget.addTab(language_widget, _("language", "Language"))
    
    def _populate_language_combo(self):
        """Populate the language combo box with available languages"""
        self.language_combo.clear()
        
        # Get installed locales
        installed_locales = self.language_manager.get_installed_locales()
        
        for locale_code, display_name in installed_locales.items():
            self.language_combo.addItem(display_name, locale_code)
        
        # Set current selection
        current_locale = get_current_locale()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_locale:
                self.language_combo.setCurrentIndex(i)
                break
    
    def _create_buttons(self, main_layout):
        """Create dialog buttons"""
        button_layout = QW.QHBoxLayout()
        button_layout.addStretch()
        
        # OK button
        self.ok_button = QW.QPushButton(_("ok", "OK"))
        self.ok_button.clicked.connect(self.accept)
        
        # Cancel button
        self.cancel_button = QW.QPushButton(_("cancel", "Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        
        # Apply button
        self.apply_button = QW.QPushButton(_("apply", "Apply"))
        self.apply_button.clicked.connect(self._apply_settings)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
    
    def _load_settings(self):
        """Load current settings"""
        try:
            # Load general settings
            settings = QC.QSettings()
            
            # Auto-save
            self.auto_save_checkbox.setChecked(
                settings.value("general/auto_save", True, type=bool)
            )
            
            # Confirm exit
            self.confirm_exit_checkbox.setChecked(
                settings.value("general/confirm_exit", True, type=bool)
            )
            
            # Theme
            theme = settings.value("display/theme", "light")
            theme_map = {"light": 0, "dark": 1, "system": 2}
            self.theme_combo.setCurrentIndex(theme_map.get(theme, 0))
            
            # Font size
            font_size = settings.value("display/font_size", 10, type=int)
            self.font_size_spinbox.setValue(font_size)
            
            # Load current language info
            current_locale = get_current_locale()
            current_language_name = self.language_manager.get_locale_info(current_locale).get("name", current_locale)
            self.current_language_label.setText(current_language_name)
            
            # Update translation status
            self._update_translation_status(current_locale)
            
            self.logger.debug("Settings loaded successfully")
            
        except Exception as e:
            self.logger.error("Failed to load settings: %s", e)
    
    def _update_translation_status(self, locale_code):
        """Update the translation status display"""
        try:
            # Get validation results
            validation = self.language_manager.validate_translations(locale_code)
            
            total_keys = len(validation)
            translated_keys = sum(1 for translated in validation.values() if translated)
            
            status_text = _(
                "translation_status_text", 
                f"Translation coverage: {translated_keys}/{total_keys} keys translated"
            )
            
            if translated_keys == total_keys:
                status_text += f"\n{_('translation_complete', '✓ Translation is complete')}"
            else:
                status_text += f"\n{_('translation_incomplete', '⚠ Some translations are missing')}"
            
            self.status_text.setText(status_text)
            
        except Exception as e:
            self.logger.error("Failed to update translation status: %s", e)
    
    def _apply_language(self):
        """Apply the selected language"""
        try:
            # Get selected locale
            current_index = self.language_combo.currentIndex()
            if current_index >= 0:
                selected_locale = self.language_combo.itemData(current_index)
                
                # Set the locale
                if self.language_manager.set_locale(selected_locale):
                    # Update current language display
                    current_language_name = self.language_manager.get_locale_info(selected_locale).get("name", selected_locale)
                    self.current_language_label.setText(current_language_name)
                    
                    # Update translation status
                    self._update_translation_status(selected_locale)
                    
                    self.logger.info("Language applied: %s", selected_locale)
                else:
                    QW.QMessageBox.warning(
                        self,
                        _("warning", "Warning"),
                        _("language_change_failed", "Failed to change language")
                    )
        
        except Exception as e:
            self.logger.error("Failed to apply language: %s", e)
            QW.QMessageBox.critical(
                self,
                _("error", "Error"),
                f"{_('language_change_error', 'Language change error')}: {str(e)}"
            )
    
    def _apply_settings(self):
        """Apply current settings"""
        try:
            settings = QC.QSettings()
            
            # Save general settings
            settings.setValue("general/auto_save", self.auto_save_checkbox.isChecked())
            settings.setValue("general/confirm_exit", self.confirm_exit_checkbox.isChecked())
            
            # Save display settings
            theme_map = {0: "light", 1: "dark", 2: "system"}
            settings.setValue("display/theme", theme_map.get(self.theme_combo.currentIndex(), "light"))
            settings.setValue("display/font_size", self.font_size_spinbox.value())
            
            # Save language preference
            current_index = self.language_combo.currentIndex()
            if current_index >= 0:
                selected_locale = self.language_combo.itemData(current_index)
                settings.setValue("language/locale", selected_locale)
            
            settings.sync()
            
            self.logger.info("Settings applied successfully")
            
            # Emit signal that preferences have been applied
            self.preferences_applied.emit()
            
            # Show confirmation
            QW.QMessageBox.information(
                self,
                _("information", "Information"),
                _("settings_applied", "Settings have been applied successfully.")
            )
            
        except Exception as e:
            self.logger.error("Failed to apply settings: %s", e)
            QW.QMessageBox.critical(
                self,
                _("error", "Error"),
                f"{_('settings_apply_error', 'Settings apply error')}: {str(e)}"
            )
    
    def accept(self):
        """Handle OK button clicked"""
        self._apply_settings()
        super().accept()
    
    
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Save any pending changes
        if hasattr(self, 'auto_save_checkbox') and self.auto_save_checkbox.isChecked():
            self._apply_settings()
        
        super().closeEvent(event)