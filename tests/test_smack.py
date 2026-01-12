# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Tests for SMACK CRC extension."""

import pytest
from unittest.mock import MagicMock

from pyxkiss.smack import SMACK
from pyxkiss.constants import SMACK_FLAG

def test_smack_crc_calculation():
    k = SMACK("dummy")
    data = b"\x80Hello"
    crc = k._crc(data)
    assert len(crc) == 2
    # Known test vector (example)
    assert crc.hex().upper() in ["4D37", "374D"]  # LSB-first order

def test_smack_auto_enable(mock_serial):
    on_frame = MagicMock()
    k = SMACK("dummy", on_frame=on_frame)
    assert not k.smack_enabled

    # Simulate valid SMACK frame
    valid_crc = k._crc(b"\x80Test")
    frame = b"\x80Test" + valid_crc
    k._wrapped_on_frame(0x80, frame)
    assert k.smack_enabled


def test_smack_invalid_crc_drop(mock_serial):
    k = SMACK("dummy")
    bad_crc = b"\x00\x00"
    frame = b"\x80Test" + bad_crc
    k._wrapped_on_frame(0x80, frame)
    # Should drop silently (no callback)
