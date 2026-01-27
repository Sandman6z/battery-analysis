import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.i18n_service import I18nService


class TestI18nService:
    def setup_method(self):
        self.service = I18nService()

    def test_get_translation(self):
        key = "test_key"
        result = self.service.get_translation(key)
        assert isinstance(result, str)

    def test_change_language(self):
        language = "en"
        result = self.service.change_language(language)
        assert result is True

    def test_get_current_language(self):
        result = self.service.get_current_language()
        assert isinstance(result, str)