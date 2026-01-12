# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Full integration tests for PyXKISS end-to-end flows."""

import pytest
from unittest.mock import MagicMock, patch, call
time.sleep = lambda x: None  # Speed up

from pyxkiss.xkiss import XKISS
from pyxkiss.constants import CMD_DATA, CMD_POLL

@pytest.fixture
def mock_serial(monkeypatch):
    class MockSerial:
        def __init__(self, *args, **kwargs):
            self.write = MagicMock()
            self.read = MagicMock(return_value=b'')
            self.close = MagicMock()
    monkeypatch.setattr('serial.Serial', MockSerial)
    return MockSerial

def test_full_flow_queue_poll_flush(mock_serial):
    on_frame = MagicMock()
    k = XKISS("dummy", polling_mode=True, max_queue_size=5, on_frame=on_frame)

    # Queue data
    k._wrapped_on_frame(CMD_DATA, b"data1")
    k._wrapped_on_frame(CMD_DATA, b"data2")
    assert k.queue_size(0) == 2

    # Poll → flush
    k._wrapped_on_frame(CMD_POLL, b"")
    assert k.queue_size(0) == 0
    assert mock_serial.write.call_count >= 2

def test_checksum_integrated_flow(mock_serial):
    k = XKISS("dummy", checksum_mode=True, polling_mode=True)
    k.send(b"test", port=1)
    assert mock_serial.write.call_count == 1
    frame = mock_serial.write.call_args[0][0]
    assert len(frame) == 7  # FEND + cmd + 4 data + checksum + FEND


def test_error_handling_serial_fail(mock_serial):
    mock_serial.write.side_effect = serial.SerialException("Mock fail")
    k = XKISS("dummy")
    with pytest.raises(Exception):
        k.send(b"test")
