import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.managers.test_profile_manager import TestProfileManager


class TestTestProfileManager:
    def setup_method(self):
        self.manager = TestProfileManager()

    def test_create_profile(self):
        profile_data = {
            "name": "Test Profile",
            "parameters": {
                "voltage": 4.2,
                "current": 0.5
            }
        }
        result = self.manager.create_profile(profile_data)
        assert isinstance(result, dict)

    def test_load_profile(self):
        profile_name = "Test Profile"
        result = self.manager.load_profile(profile_name)
        assert isinstance(result, dict)

    def test_save_profile(self):
        profile_data = {
            "name": "Test Profile",
            "parameters": {}
        }
        result = self.manager.save_profile(profile_data)
        assert result is True

    def test_list_profiles(self):
        result = self.manager.list_profiles()
        assert isinstance(result, list)