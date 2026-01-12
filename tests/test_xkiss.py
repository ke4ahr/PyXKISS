# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Unit/integration tests for XKISS extended features."""

import pytest
from unittest.mock import MagicMock, patch, call
time.sleep = lambda x: None  # Speed up polling tests

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

def test_xkiss_polling_active(mock_serial):
    k = XKISS("dummy", polling_mode=True, poll_interval=0.01)
    time.sleep(0.05)  # Trigger a few polls
    assert k.poll_interval == 0.01
    assert mock_serial.write.call_count > 0

def test_xkiss_passive_queue_and_flush(mock_serial):
    on_frame = MagicMock()
    k = XKISS("dummy", polling_mode=True, max_queue_size=5, on_frame=on_frame)

    # Queue 3 frames
    k._wrapped_on_frame(CMD_DATA, b"d1")
    k._wrapped_on_frame(CMD_DATA, b"d2")
    k._wrapped_on_frame(CMD_DATA, b"d3")
    assert k.queue_size(0) == 3

    # Simulate external poll
    k._wrapped_on_frame(CMD_POLL, b"")
    assert k.queue_size(0) == 0
    assert mock_serial.write.call_count >= 3


def test_queue_overflow(mock_serial):
    k = XKISS("dummy", polling_mode=True, max_queue_size=2)
    k._wrapped_on_frame(CMD_DATA, b"1")
    k._wrapped_on_frame(CMD_DATA, b"2")
    k._wrapped_on_frame(CMD_DATA, b"3")  # Overflow
    assert k.queue_size(0) == 2


def test_checksum_enabled_send(mock_serial):
    k = XKISS("dummy", checksum_mode=True)
    k.send(b"\x01\x02", port=0)
    frame = mock_serial.write.call_args[0][0]
    assert len(frame) == 6  # FEND + cmd + 2 data + checksum + FEND
    checksum = frame[-2]
    assert checksum == (0x00 ^ 0x01 ^ 0x02) & 0xFF


def test_checksum_error_drop(mock_serial):
    k = XKISS("dummy", checksum_mode=True)
    bad = bytearray([0x00, 0xAA, 0xBB, 0xFF])  # Wrong checksum
    k._wrapped_on_frame(0x00, bad)
    assert mock_serial.write.call_count == 0
