from unittest.mock import Mock

import pytest
from PyQt6.QtCore import QSettings

from battery_analysis.ui.styles.theme_settings import load_theme_preference, normalize_theme


@pytest.mark.parametrize(
    ("stored", "expected"),
    [
        ("light", "light"), ("dark", "dark"), ("system", "system"),
        ("modern", "light"), (" DARK ", "dark"),
        ("unknown", "light"), (None, "light"), (42, "light"),
        (["dark"], "light"),
    ],
)
def test_normalize_theme(stored, expected):
    assert normalize_theme(stored) == expected


def test_legacy_setting_is_migrated_once(tmp_path, caplog):
    settings = QSettings(str(tmp_path / "theme.ini"), QSettings.Format.IniFormat)
    settings.setValue("display/theme", "modern")
    assert load_theme_preference(settings) == "light"
    assert settings.value("display/theme") == "light"
    assert load_theme_preference(settings) == "light"
    assert "Unknown theme" not in caplog.text


@pytest.mark.parametrize("theme", ["light", "dark", "system"])
def test_valid_preference_is_not_rewritten(theme):
    settings = Mock()
    settings.value.return_value = theme
    assert load_theme_preference(settings) == theme
    settings.setValue.assert_not_called()
