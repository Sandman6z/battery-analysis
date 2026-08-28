#!/usr/bin/env python3
"""
Preferences Dialog Module

This module implements the preferences dialog for language and other application settings.
"""

import logging
import os

import PyQt6.QtCore as QC
import PyQt6.QtWidgets as QW

from battery_analysis.i18n import _, get_current_locale
from battery_analysis.i18n.language_manager import get_language_manager
from battery_analysis.main.ui_components.config_path_provider import IConfigPathProvider


class PreferencesDialog(QW.QDialog):
    """Preferences dialog for application settings"""

    # Signal emitted when preferences are applied
    preferences_applied = QC.pyqtSignal()

    def __init__(self, parent=None, config_provider: IConfigPathProvider | None = None):
        """Initialize the preferences dialog"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Get language manager
        self.language_manager = get_language_manager()
        self._config_provider = config_provider

        # Set dialog properties
        self.setWindowTitle(_("Preferences"))
        self.setModal(True)
        self.setMinimumSize(500, 400)

        # Initialize attributes
        self.confirm_exit_checkbox = None
        self.theme_combo = None
        self.font_size_spinbox = None
        self.current_language_label = None
        self.language_combo = None
        self.status_text = None
        self.ok_button = None
        self.cancel_button = None
        self.apply_button = None
        self.tab_widget = None

        # Config tab attributes
        self.config_path_label = None
        self.config_path_lineedit = None
        self.config_browse_button = None
        self.config_validate_button = None
        self.config_status_label = None

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

        # Create Config tab
        self._create_config_tab()

        # Create buttons
        self._create_buttons(main_layout)

    def _create_general_tab(self):
        """Create the general preferences tab"""
        general_widget = QW.QWidget()
        general_layout = QW.QVBoxLayout(general_widget)

        # General settings group
        general_group = QW.QGroupBox(_("General Settings"))
        general_group_layout = QW.QVBoxLayout(general_group)

        # Confirmation on exit
        self.confirm_exit_checkbox = QW.QCheckBox(_("Confirm before exiting"))
        self.confirm_exit_checkbox.setToolTip(
            _("Show confirmation dialog when exiting the application")
        )
        general_group_layout.addWidget(self.confirm_exit_checkbox)

        general_layout.addWidget(general_group)

        # Display settings group
        display_group = QW.QGroupBox(_("Display Settings"))
        display_group_layout = QW.QVBoxLayout(display_group)

        # Theme selection
        theme_layout = QW.QHBoxLayout()
        theme_layout.addWidget(QW.QLabel(_("Theme:")))
        self.theme_combo = QW.QComboBox()
        self.theme_combo.addItems([_("Light"), _("Dark"), _("System")])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        display_group_layout.addLayout(theme_layout)

        # Font size
        font_layout = QW.QHBoxLayout()
        font_layout.addWidget(QW.QLabel(_("Font Size:")))
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
        self.tab_widget.addTab(general_widget, _("General"))

    def _create_language_tab(self):
        """Create the language preferences tab"""
        language_widget = QW.QWidget()
        language_layout = QW.QVBoxLayout(language_widget)

        # Language selection group
        language_group = QW.QGroupBox(_("Language Settings"))
        language_group_layout = QW.QVBoxLayout(language_group)

        # Current language display
        current_lang_layout = QW.QHBoxLayout()
        current_lang_layout.addWidget(QW.QLabel(_("Current Language:")))
        self.current_language_label = QW.QLabel()
        current_lang_layout.addWidget(self.current_language_label)
        current_lang_layout.addStretch()
        language_group_layout.addLayout(current_lang_layout)

        # Language selection
        lang_selection_layout = QW.QHBoxLayout()
        lang_selection_layout.addWidget(QW.QLabel(_("Select Language:")))
        self.language_combo = QW.QComboBox()
        self._populate_language_combo()
        lang_selection_layout.addWidget(self.language_combo)
        lang_selection_layout.addStretch()
        language_group_layout.addLayout(lang_selection_layout)

        # Apply button
        apply_lang_button = QW.QPushButton(_("Apply Language"))
        apply_lang_button.clicked.connect(self._apply_language)
        language_group_layout.addWidget(apply_lang_button)

        language_layout.addWidget(language_group)

        # Translation status group
        status_group = QW.QGroupBox(_("Translation Status"))
        status_layout = QW.QVBoxLayout(status_group)

        # Status text
        self.status_text = QW.QLabel(_("Translation information will be displayed here."))
        self.status_text.setWordWrap(True)
        status_layout.addWidget(self.status_text)

        language_layout.addWidget(status_group)

        # Add stretch
        language_layout.addStretch()

        # Add tab
        self.tab_widget.addTab(language_widget, _("Language"))

    def _create_config_tab(self):
        """Create the configuration file settings tab"""
        config_widget = QW.QWidget()
        config_layout = QW.QVBoxLayout(config_widget)

        # Config file path group
        config_group = QW.QGroupBox(_("Configuration File Settings"))
        config_group_layout = QW.QVBoxLayout(config_group)

        # Current config path display
        current_path_layout = QW.QHBoxLayout()
        current_path_layout.addWidget(QW.QLabel(_("Current Config Path:")))
        self.config_path_label = QW.QLabel(_("Not loaded"))
        self.config_path_label.setStyleSheet("color: gray;")
        current_path_layout.addWidget(self.config_path_label, 1)
        config_group_layout.addLayout(current_path_layout)

        # Config path selection
        path_layout = QW.QHBoxLayout()
        path_layout.addWidget(QW.QLabel(_("Custom Config Path:")))
        self.config_path_lineedit = QW.QLineEdit()
        self.config_path_lineedit.setPlaceholderText(_("Enter custom configuration file path..."))
        self.config_browse_button = QW.QPushButton(_("Browse..."))
        self.config_browse_button.clicked.connect(self._browse_config_file)
        path_layout.addWidget(self.config_path_lineedit, 1)
        path_layout.addWidget(self.config_browse_button)
        config_group_layout.addLayout(path_layout)

        # Validate button
        validate_layout = QW.QHBoxLayout()
        self.config_validate_button = QW.QPushButton(_("Validate Configuration"))
        self.config_validate_button.clicked.connect(self._validate_config_file)
        self.config_status_label = QW.QLabel()
        self.config_status_label.setWordWrap(True)
        validate_layout.addWidget(self.config_validate_button)
        validate_layout.addWidget(self.config_status_label, 1)
        config_group_layout.addLayout(validate_layout)

        config_layout.addWidget(config_group)

        # Required sections info
        info_group = QW.QGroupBox(_("Required Sections in Config File"))
        info_layout = QW.QVBoxLayout(info_group)

        required_sections = [
            "battery — Battery type, specification types, rules",
            "test — Tester locations, tested by, equipment",
        ]
        for section in required_sections:
            info_layout.addWidget(QW.QLabel(f"• {section}"))

        info_layout.addStretch()
        config_layout.addWidget(info_group)

        # Reset to default button
        reset_layout = QW.QHBoxLayout()
        reset_button = QW.QPushButton(_("Reset to Default"))
        reset_button.clicked.connect(self._reset_config_path)
        reset_layout.addWidget(reset_button)
        reset_layout.addStretch()
        config_layout.addLayout(reset_layout)

        # Add stretch
        config_layout.addStretch()

        # Add tab
        self.tab_widget.addTab(config_widget, _("Config"))

    def _browse_config_file(self):
        """Open file dialog to browse for config file"""
        file_path, filter_ = QW.QFileDialog.getOpenFileName(
            self,
            _("Select Configuration File"),
            "",
            "JSON Files (*.json);;INI Files (*.ini);;All Files (*)",
        )
        if file_path:
            self.config_path_lineedit.setText(file_path)
            self._validate_config_file()

    def _validate_config_file(self):
        """Validate the selected configuration file"""
        file_path = self.config_path_lineedit.text().strip()

        if not file_path:
            self.config_status_label.setText(_("Please enter a configuration file path"))
            self.config_status_label.setStyleSheet("color: orange;")
            return

        if not os.path.exists(file_path):
            self.config_status_label.setText(_("File does not exist"))
            self.config_status_label.setStyleSheet("color: red;")
            return

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".json":
                import json

                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    self.config_status_label.setText(_("JSON root must be an object"))
                    self.config_status_label.setStyleSheet("color: red;")
                    return
                required_keys = ["battery", "test"]
                missing = [k for k in required_keys if k not in data]
                if missing:
                    self.config_status_label.setText(f"Missing required keys: {', '.join(missing)}")
                    self.config_status_label.setStyleSheet("color: orange;")
                else:
                    self.config_status_label.setText(_("Configuration file is valid!"))
                    self.config_status_label.setStyleSheet("color: green;")
            else:
                # INI 文件兼容验证（已弃用，仅用于旧版兼容）
                import configparser

                parser = configparser.ConfigParser()
                parser.read(file_path, encoding="utf-8")

                required_sections = ["BatteryConfig", "TestConfig", "PltConfig"]
                missing_sections = [s for s in required_sections if not parser.has_section(s)]

                if missing_sections:
                    self.config_status_label.setText(
                        _(f"Missing required sections: {', '.join(missing_sections)}")
                    )
                    self.config_status_label.setStyleSheet("color: orange;")
                else:
                    self.config_status_label.setText(
                        _("INI format is deprecated; consider migrating to config.json")
                    )
                    self.config_status_label.setStyleSheet("color: orange;")

        except Exception as e:
            self.config_status_label.setText(_(f"Error parsing config: {e!s}"))
            self.config_status_label.setStyleSheet("color: red;")

    def _reset_config_path(self):
        """Reset config path to default"""
        self.config_path_lineedit.clear()
        self.config_status_label.setText("")
        settings = QC.QSettings()
        settings.remove("config/custom_config_path")
        # 同步清除模块级缓存，确保 config_utils 不再返回旧路径
        from battery_analysis.utils.config_utils import clear_custom_config_path

        clear_custom_config_path()

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
        self.ok_button = QW.QPushButton(_("OK"))
        self.ok_button.clicked.connect(self.accept)

        # Cancel button
        self.cancel_button = QW.QPushButton(_("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        # Apply button
        self.apply_button = QW.QPushButton(_("Apply"))
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
            current_language_name = self.language_manager.get_locale_info(current_locale).get(
                "name", current_locale
            )
            self.current_language_label.setText(current_language_name)

            # Update translation status
            self._update_translation_status(current_locale)

            # Load config path settings
            custom_config_path = settings.value("config/custom_config_path", "", type=str)
            self.config_path_lineedit.setText(custom_config_path)

            # Display current active config path
            if self._config_provider is not None:
                try:
                    cfg_path = self._config_provider.get_config_path()
                    if cfg_path:
                        self.config_path_label.setText(cfg_path)
                        self.config_path_label.setStyleSheet("color: green;")
                    else:
                        self.config_path_label.setText(_("Using default paths"))
                        self.config_path_label.setStyleSheet("color: gray;")
                except Exception:
                    self.config_path_label.setText(_("Not loaded"))
                    self.config_path_label.setStyleSheet("color: gray;")
            else:
                self.config_path_label.setText(_("Not loaded"))
                self.config_path_label.setStyleSheet("color: gray;")

            self.logger.debug("Settings loaded successfully")

        except (OSError, ValueError, ImportError, AttributeError) as e:
            self.logger.error("Failed to load settings: %s", e)

    def _update_translation_status(self, locale_code):
        """Update the translation status display"""
        try:
            # Get validation results
            validation = self.language_manager.validate_translations(locale_code)

            total_keys = len(validation)
            translated_keys = sum(1 for translated in validation.values() if translated)

            status_text = _(f"Translation coverage: {translated_keys}/{total_keys} keys translated")

            if translated_keys == total_keys:
                status_text += f"\n{_('✓ Translation is complete')}"
            else:
                status_text += f"\n{_('⚠ Some translations are missing')}"

            self.status_text.setText(status_text)

        except (OSError, ValueError, AttributeError) as e:
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
                    current_language_name = self.language_manager.get_locale_info(
                        selected_locale
                    ).get("name", selected_locale)
                    self.current_language_label.setText(current_language_name)

                    # Update translation status
                    self._update_translation_status(selected_locale)

                    self.logger.info("Language applied: %s", selected_locale)
                else:
                    QW.QMessageBox.warning(self, _("Warning"), _("Failed to change language"))

        except (OSError, ValueError, AttributeError, TypeError) as e:
            self.logger.error("Failed to apply language: %s", e)
            QW.QMessageBox.critical(self, _("Error"), f"{_('Language change error')}: {e!s}")

    def _apply_settings(self):
        """Apply current settings"""
        try:
            settings = QC.QSettings()

            # Save general settings
            settings.setValue("general/confirm_exit", self.confirm_exit_checkbox.isChecked())

            # Save display settings
            theme_map = {0: "light", 1: "dark", 2: "system"}
            settings.setValue(
                "display/theme", theme_map.get(self.theme_combo.currentIndex(), "light")
            )
            settings.setValue("display/font_size", self.font_size_spinbox.value())

            # Save language preference
            current_index = self.language_combo.currentIndex()
            if current_index >= 0:
                selected_locale = self.language_combo.itemData(current_index)
                settings.setValue("language/locale", selected_locale)

            # Save custom config path
            custom_path = self.config_path_lineedit.text().strip()
            self.logger.debug(f"Saving custom config path: '{custom_path}'")
            if custom_path:
                if os.path.exists(custom_path):
                    settings.setValue("config/custom_config_path", custom_path)
                    self.logger.debug(f"Saved custom config path: '{custom_path}'")
                else:
                    self.logger.warning(f"Config file does not exist: '{custom_path}'")
                    settings.setValue("config/custom_config_path", custom_path)
                    self.logger.debug(f"Saved config path (file does not exist): '{custom_path}'")
            else:
                settings.remove("config/custom_config_path")

            settings.sync()
            self.logger.info("Settings applied successfully")

            # Emit signal that preferences have been applied
            self.preferences_applied.emit()

        except (OSError, ValueError, AttributeError, TypeError) as e:
            self.logger.error("Failed to apply settings: %s", e)
            QW.QMessageBox.critical(self, _("Error"), f"{_('Settings apply error')}: {e!s}")

    def accept(self):
        """Handle OK button clicked — apply settings once then close"""
        self._apply_settings()
        super().accept()

    def reject(self):
        """Handle Cancel / Escape — close without saving"""
        super().reject()

    def closeEvent(self, event):
        """Handle dialog close event (e.g. X button) — same as Cancel, no auto-save"""
        super().closeEvent(event)
