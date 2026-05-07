from unittest.mock import Mock, patch
from battery_analysis.main.services.i18n_service import I18nService


class TestI18nService:
    def setup_method(self):
        self.service = I18nService()

    def test_get_current_language(self):
        result = self.service.get_current_language()
        assert isinstance(result, str)

    def test_get_available_languages(self):
        result = self.service.get_available_languages()
        assert isinstance(result, list)