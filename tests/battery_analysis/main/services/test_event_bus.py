import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.event_bus import EventBus


class TestEventBus:
    def setup_method(self):
        self.event_bus = EventBus()

    def test_subscribe(self):
        event_name = "test_event"
        callback = Mock()
        result = self.event_bus.subscribe(event_name, callback)
        assert result is True

    def test_unsubscribe(self):
        event_name = "test_event"
        callback = Mock()
        self.event_bus.subscribe(event_name, callback)
        result = self.event_bus.unsubscribe(event_name, callback)
        assert result is True

    def test_publish(self):
        event_name = "test_event"
        callback = Mock()
        self.event_bus.subscribe(event_name, callback)
        event_data = {"data": "test"}
        self.event_bus.publish(event_name, event_data)
        callback.assert_called_once_with(event_data)