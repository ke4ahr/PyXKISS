# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""SMACK (Stuttgart Modified Amateurradio CRC-KISS) extension layer.

Adds CRC-16 to data frames (command bit 7 set), auto-switch on first valid CRC frame.
Builds on XKISS for multi-drop and polling compatibility.
"""

from .xkiss import XKISS
from .constants import SMACK_FLAG, SMACK_POLY, SMACK_INIT
from typing import Callable, Optional

class SMACK(XKISS):
    """SMACK extension: adds CRC-16 protection to data frames."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._smack_enabled = False
        self._lock = threading.Lock()
        # Wrap user callback to handle SMACK
        user_callback = kwargs.get('on_frame')
        self.on_xframe = self._smack_callback_wrapper(user_callback)

    def _smack_callback_wrapper(self, user_callback: Optional[Callable]):
        def wrapper(addr: int, port: int, payload: bytes):
            cmd = payload[0] if payload else 0x00
            data = payload[1:] if len(payload) > 1 else b''

            if cmd & SMACK_FLAG:
                with self._lock:
                    self._smack_enabled = True
                if len(data) < 2:
                    return
                received_crc = data[-2:]
                computed = self._crc(bytes([cmd]) + data[:-2])
                if received_crc != computed:
                    logger.warning("SMACK CRC invalid - frame dropped")
                    return
                data = data[:-2]

            if user_callback:
                user_callback(addr, port, data)
        return wrapper

    def send(self, payload: bytes, port: int = 0, cmd: int = CMD_DATA):
        if self._smack_enabled:
            cmd |= SMACK_FLAG
            crc = self._crc(bytes([cmd]) + payload)
            payload += crc  # LSB-first
        super().send(payload, port, cmd)

    def _crc(self, data: bytes) -> bytes:
        """Compute SMACK CRC-16 (poly 0x8005 normal, init 0x0000)."""
        crc = SMACK_INIT
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                crc = (crc << 1) ^ SMACK_POLY if crc & 0x8000 else crc << 1
                crc &= 0xFFFF
        return crc.to_bytes(2, 'little')

    @property
    def smack_enabled(self):
        return self._smack_enabled
