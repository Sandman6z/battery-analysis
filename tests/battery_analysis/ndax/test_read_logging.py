"""NDA reads must request quiet logging without hiding warnings or parse errors."""

import logging
from unittest.mock import Mock

import pytest

from battery_analysis.ndax import converter, reader


@pytest.mark.parametrize("read_file", [reader.read_analysis_views, converter.convert_one])
def test_nda_read_keeps_warnings_and_errors(tmp_path, monkeypatch, caplog, read_file):
    path = tmp_path / "sample.ndax"
    path.touch()
    nda_logger = logging.getLogger("newarenda")
    old_level = nda_logger.level

    def fail_read(*args, **kwargs):
        # NewareNDA.read resets its logger level on every call.
        nda_logger.setLevel(kwargs.get("log_level", "INFO"))
        nda_logger.info("Server version: noisy per-file metadata")
        nda_logger.warning("A real data warning")
        raise ValueError("parse failure")

    read = Mock(side_effect=fail_read)
    monkeypatch.setattr(reader.nda, "read", read)
    try:
        with caplog.at_level(logging.INFO), pytest.raises(ValueError, match="parse failure"):
            read_file(path)
        read.assert_called_once_with(str(path), software_cycle_number=False, log_level="WARNING")
        assert "Server version" not in caplog.text
        assert "A real data warning" in caplog.text
    finally:
        nda_logger.setLevel(old_level)
