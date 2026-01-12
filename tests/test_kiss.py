# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Unit tests for base KISS class."""

import pytest
from unittest.mock import MagicMock, patch

from pyxkiss.kiss import KISS
from pyxkiss.constants import FEND, FESC, TFEND, TFESC, CMD_DATA

@pytest.fixture
def mock_serial(monkeypatch):
    class MockSerial:
        def __init__(self, *args, **kwargs):
            self.write = MagicMock()
            self.read = MagicMock(return_value=b'')
            self.close = MagicMock()
    monkeypatch.setattr('serial.Serial', MockSerial)
    return MockSerial

def test_kiss_init(mock_serial):
    k = KISS("dummy")
    assert k.serial is not None


def test_send_basic(mock_serial):
    k = KISS("dummy")
    payload = b"test"
    k.send(payload)
    mock_serial.write.assert_called_once()
    frame = mock_serial.write.call_args[0][0]
    assert frame.startswith(bytes([FEND, CMD_DATA]))
    assert frame.endswith(bytes([FEND]))


def test_send_with_escape(mock_serial):
    k = KISS("dummy")
    payload = bytes([FEND, FESC, 0x41])
    k.send(payload)
    frame = mock_serial.write.call_args[0][0]
    assert b'\xc0\xdb\xdc' in frame  # Escaped FEND
    assert b'\xc0\xdb\xdd' in frame  # Escaped FESC


def test_invalid_command(mock_serial):
    k = KISS("dummy")
    with pytest.raises(ValueError):
        k.send(b"", cmd=0x10)  # Invalid cmd


def test_set_param(mock_serial):
    k = KISS("dummy")
    k.set_param(CMD_TXDELAY, 50)
    mock_serial.write.assert_called_once()
    frame = mock_serial.write.call_args[0][0]
    assert frame[1] == CMD_TXDELAY
    assert frame[2] == 50
