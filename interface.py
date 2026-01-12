# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Shared serial interface base class for KISS family implementations.

Handles low-level serial I/O and threaded receive loop.
"""

import serial
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SerialInterface:
    """Base class for serial-based KISS protocols."""

    def __init__(self, device: str, baudrate: int = 9600):
        try:
            self.serial = serial.Serial(device, baudrate, timeout=1)
        except serial.SerialException as e:
            logger.critical(f"Failed to open {device}: {e}")
            raise

        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()
        logger.debug(f"SerialInterface started on {device} @ {baudrate} baud")

    def _receive_loop(self):
        """Background thread to read serial data."""
        while self._running:
            try:
                data = self.serial.read(1024)
                if data:
                    for byte in data:
                        self._process_byte(byte)
            except serial.SerialException as e:
                logger.error(f"Serial read error: {e}")
                time.sleep(1)  # Backoff
            except Exception as e:
                logger.exception(f"Unexpected receive error: {e}")
                break

    def _process_byte(self, byte: int):
        """Override in subclass to process incoming bytes."""
        raise NotImplementedError("_process_byte must be implemented by subclass")

    def write(self, data: bytes):
        """Write bytes to serial port."""
        try:
            self.serial.write(data)
        except serial.SerialException as e:
            logger.error(f"Serial write error: {e}")
            raise

    def close(self):
        """Graceful shutdown."""
        self._running = False
        if self.serial.is_open:
            self.serial.close()
        logger.debug("SerialInterface closed")
