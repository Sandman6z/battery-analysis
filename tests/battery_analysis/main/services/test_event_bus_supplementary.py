"""
Event bus supplementary tests — covers Event, EventBus singleton, error paths,
and edge cases not in the existing test_event_bus.py.
"""

import time
from unittest.mock import Mock, patch, MagicMock, PropertyMock

import pytest

from battery_analysis.main.services.event_bus import EventBus, Event, EventType


# ---------------------------------------------------------------------------
# TestEvent
# ---------------------------------------------------------------------------

class TestEvent:
    """Event class unit tests"""

    def test_constructor_sets_attributes(self):
        ev = Event(EventType.CONFIG_CHANGED, {"key": "val"})
        assert ev.event_type == EventType.CONFIG_CHANGED
        assert ev.data == {"key": "val"}
        assert isinstance(ev.timestamp, float)
        assert isinstance(ev.event_id, int)

    def test_constructor_with_none_data(self):
        ev = Event(EventType.PROGRESS_UPDATED)
        assert ev.data is None

    def test_timestamp_is_recent(self):
        before = time.time()
        ev = Event(EventType.STATUS_CHANGED)
        assert before <= ev.timestamp <= time.time() + 1

    def test_event_id_unique(self):
        ev1 = Event(EventType.ANALYSIS_COMPLETED)
        ev2 = Event(EventType.ANALYSIS_COMPLETED)
        assert ev1.event_id != ev2.event_id

    def test_str_representation(self):
        ev = Event(EventType.PROGRESS_UPDATED, 42)
        s = str(ev)
        assert "PROGRESS_UPDATED" in s
        assert "42" in s


# ---------------------------------------------------------------------------
# TestEventBusSingleton
# ---------------------------------------------------------------------------

class TestEventBusSingleton:
    """EventBus singleton pattern tests"""

    def test_get_instance_returns_same_instance(self):
        instance1 = EventBus.get_instance()
        instance2 = EventBus.get_instance()
        assert instance1 is instance2

    def test_get_instance_creates_on_first_call(self):
        # Reset the singleton
        EventBus._instance = None
        instance = EventBus.get_instance()
        assert instance is not None
        assert isinstance(instance, EventBus)


# ---------------------------------------------------------------------------
# TestEventBusSubscribe
# ---------------------------------------------------------------------------

class TestEventBusSubscribe:
    """EventBus.subscribe tests"""

    def test_subscribe_adds_callback(self):
        eb = EventBus()
        cb = Mock()
        eb.subscribe(EventType.CONFIG_CHANGED, cb)
        assert cb in eb._subscribers[EventType.CONFIG_CHANGED]

    def test_subscribe_returns_true(self):
        eb = EventBus()
        assert eb.subscribe(EventType.CONFIG_CHANGED, Mock()) is True

    def test_multiple_subscribers_same_event(self):
        eb = EventBus()
        cb1 = Mock()
        cb2 = Mock()
        eb.subscribe(EventType.CONFIG_CHANGED, cb1)
        eb.subscribe(EventType.CONFIG_CHANGED, cb2)
        assert len(eb._subscribers[EventType.CONFIG_CHANGED]) == 2

    def test_subscribe_type_error_returns_false(self):
        eb = EventBus()
        # Replace _subscribers with a non-dict that raises TypeError on __contains__
        class BadContainer:
            def __contains__(self, key):
                raise TypeError("corrupt")
            def __getitem__(self, key):
                raise TypeError("corrupt")
            def __setitem__(self, key, val):
                raise TypeError("corrupt")
        eb._subscribers = BadContainer()
        result = eb.subscribe(EventType.CONFIG_CHANGED, Mock())
        assert result is False


# ---------------------------------------------------------------------------
# TestEventBusUnsubscribe
# ---------------------------------------------------------------------------

class TestEventBusUnsubscribe:
    """EventBus.unsubscribe tests"""

    def test_unsubscribe_removes_callback(self):
        eb = EventBus()
        cb = Mock()
        eb.subscribe(EventType.CONFIG_CHANGED, cb)
        eb.unsubscribe(EventType.CONFIG_CHANGED, cb)
        assert cb not in eb._subscribers[EventType.CONFIG_CHANGED]

    def test_unsubscribe_returns_true_on_success(self):
        eb = EventBus()
        cb = Mock()
        eb.subscribe(EventType.CONFIG_CHANGED, cb)
        assert eb.unsubscribe(EventType.CONFIG_CHANGED, cb) is True

    def test_unsubscribe_returns_false_when_not_found(self):
        eb = EventBus()
        result = eb.unsubscribe(EventType.CONFIG_CHANGED, Mock())
        assert result is False

    def test_unsubscribe_returns_false_when_no_subscribers(self):
        eb = EventBus()
        result = eb.unsubscribe(EventType.FILE_SELECTED, Mock())
        assert result is False

    def test_unsubscribe_type_error_returns_false(self):
        eb = EventBus()
        class BadContainer:
            def __contains__(self, key):
                raise TypeError("corrupt")
            def __getitem__(self, key):
                raise TypeError("corrupt")
        eb._subscribers = BadContainer()
        result = eb.unsubscribe(EventType.CONFIG_CHANGED, Mock())
        assert result is False


# ---------------------------------------------------------------------------
# TestEventBusEmit
# ---------------------------------------------------------------------------

class TestEventBusEmit:
    """EventBus.emit tests"""

    def test_emit_calls_subscriber(self):
        eb = EventBus()
        cb = Mock()
        eb.subscribe(EventType.CONFIG_CHANGED, cb)
        eb.emit(EventType.CONFIG_CHANGED, "data")
        cb.assert_called_once()
        event_arg = cb.call_args[0][0]
        assert isinstance(event_arg, Event)
        assert event_arg.event_type == EventType.CONFIG_CHANGED
        assert event_arg.data == "data"

    def test_emit_with_no_subscribers_does_not_raise(self):
        eb = EventBus()
        eb.emit(EventType.ANALYSIS_COMPLETED)  # should not raise

    def test_emit_calls_all_subscribers(self):
        eb = EventBus()
        cb1 = Mock()
        cb2 = Mock()
        eb.subscribe(EventType.STATUS_CHANGED, cb1)
        eb.subscribe(EventType.STATUS_CHANGED, cb2)
        eb.emit(EventType.STATUS_CHANGED)
        cb1.assert_called_once()
        cb2.assert_called_once()

    def test_emit_only_calls_subscribers_of_event_type(self):
        eb = EventBus()
        cb = Mock()
        eb.subscribe(EventType.CONFIG_CHANGED, cb)
        eb.emit(EventType.ANALYSIS_COMPLETED)
        cb.assert_not_called()

    def test_callback_error_does_not_prevent_other_callbacks(self):
        eb = EventBus()
        cb_ok = Mock()
        cb_bad = Mock(side_effect=ValueError("boom"))
        eb.subscribe(EventType.STATUS_CHANGED, cb_bad)
        eb.subscribe(EventType.STATUS_CHANGED, cb_ok)
        eb.emit(EventType.STATUS_CHANGED, "data")
        cb_ok.assert_called_once()

    def test_emit_type_error_does_not_raise(self):
        eb = EventBus()
        # Make Event construction raise TypeError
        with patch("battery_analysis.main.services.event_bus.Event", side_effect=TypeError("bad")):
            eb.emit(EventType.CONFIG_CHANGED)  # should not raise


# ---------------------------------------------------------------------------
# TestEventBusProcessEvent
# ---------------------------------------------------------------------------

class TestEventBusProcessEvent:
    """EventBus._process_event — internal event processing"""

    def test_process_event_calls_no_callbacks_when_no_subscribers(self):
        eb = EventBus()
        ev = Event(EventType.ANALYSIS_COMPLETED)
        eb._process_event(ev)  # should not raise

    def test_single_bad_callback_is_logged(self):
        eb = EventBus()
        cb = Mock(side_effect=TypeError("bad"))
        eb.subscribe(EventType.CONFIG_CHANGED, cb)
        ev = Event(EventType.CONFIG_CHANGED)
        eb._process_event(ev)  # should not raise (error logged internally)

    def test_process_event_error_on_invalid_subscribers(self):
        eb = EventBus()
        # _subscribers accesses on a non-dict raise TypeError
        eb._subscribers = object()
        eb._process_event(Event(EventType.CONFIG_CHANGED))  # should not raise


# ---------------------------------------------------------------------------
# TestEventType
# ---------------------------------------------------------------------------

class TestEventType:
    def test_all_event_types_defined(self):
        expected = [
            "PROGRESS_UPDATED",
            "STATUS_CHANGED",
            "ANALYSIS_COMPLETED",
            "VISUALIZER_REQUESTED",
            "CONFIG_CHANGED",
            "FILE_SELECTED",
        ]
        assert sorted(expected) == sorted(et.name for et in EventType)
