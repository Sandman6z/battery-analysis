from unittest.mock import Mock, patch
from battery_analysis.main.services.event_bus import EventBus, EventType


class TestEventBus:
    def setup_method(self):
        self.event_bus = EventBus()

    def test_subscribe(self):
        callback = Mock()
        result = self.event_bus.subscribe(EventType.CONFIG_CHANGED, callback)
        assert result is True

    def test_unsubscribe(self):
        callback = Mock()
        self.event_bus.subscribe(EventType.CONFIG_CHANGED, callback)
        result = self.event_bus.unsubscribe(EventType.CONFIG_CHANGED, callback)
        assert result is True

    def test_emit(self):
        callback = Mock()
        self.event_bus.subscribe(EventType.CONFIG_CHANGED, callback)
        self.event_bus.emit(EventType.CONFIG_CHANGED, {"key": "test", "value": 1})
        callback.assert_called_once()
