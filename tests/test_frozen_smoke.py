"""Frozen startup smoke mode must wait for completed main-window initialization."""

import sys
from unittest.mock import Mock

import pytest


def test_smoke_mode_waits_for_initialized_window(monkeypatch):
    from battery_analysis.main import main_window

    app = Mock()
    window = Mock()
    window._lazy_init_done = False
    window.actionConfiguration.isEnabled.return_value = False
    timer = Mock()
    monkeypatch.setattr(sys, "argv", ["battery-analyzer", "--smoke-test"])
    monkeypatch.setattr(main_window, "Main", Mock(return_value=window))
    monkeypatch.setattr(main_window.QC, "QTimer", Mock(return_value=timer))

    def run_event_loop():
        callback = timer.timeout.connect.call_args.args[0]
        callback()
        app.exit.assert_not_called()
        window._lazy_init_done = True
        callback()
        app.exit.assert_not_called()
        window.actionConfiguration.isEnabled.return_value = True
        callback()
        app.exit.assert_called_once_with(0)
        return 0

    app.exec.side_effect = run_event_loop
    with pytest.raises(SystemExit) as result:
        main_window.main(app=app, splash=Mock())
    assert result.value.code == 0
    timer.start.assert_called_once_with(100)


def test_normal_startup_does_not_enable_smoke_timer(monkeypatch):
    from battery_analysis.main import main_window

    app = Mock()
    app.exec.return_value = 0
    timer = Mock()
    monkeypatch.setattr(sys, "argv", ["battery-analyzer"])
    monkeypatch.setattr(main_window, "Main", Mock())
    monkeypatch.setattr(main_window.QC, "QTimer", timer)
    with pytest.raises(SystemExit) as result:
        main_window.main(app=app, splash=Mock())
    assert result.value.code == 0
    timer.assert_not_called()
