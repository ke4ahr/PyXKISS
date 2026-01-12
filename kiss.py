# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Base class for standard KISS protocol.

Handles framing, escaping/destuffing, threaded receive loop,
and basic command sending (0x00-0x06, 0xFF).
"""

import serial
import threading
import logging
from typing import Callable, Optional

from .constants import FEND, FESC, TFEND, TFESC, CMD_DATA, CMD_TXDELAY, \
    CMD_PERSIST, CMD_SLOTTIME, CMD_TXTAIL, CMD_FULLDUP, CMD_HARDWARE, CMD_EXIT
from .exceptions import SerialError

logger = logging.getLogger(__name__)

class KISS:
    """Standard KISS protocol implementation for serial TNC."""

    def __init__(
        self,
        device: str,
        baudrate: int = 9600,
        on_frame: Optional[Callable[[int, bytes], None]] = None,
    ):
        """Initialize serial connection and receive thread."""
        try:
            self.serial = serial.Serial(device, baudrate, timeout=1)
        except serial.SerialException as e:
            logger.critical(f"Failed to open serial port {device}: {e}")
            raise SerialError(f"Serial open failed: {e}")

        self.on_frame = on_frame  # callback(cmd: int, payload: bytes)
        self.buffer = bytearray()
        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

        logger.info(f"KISS initialized on {device} @ {baudrate} baud")

    def send(self, payload: bytes, cmd: int = CMD_DATA):
        """Send a KISS frame with given command byte."""
        valid_cmds = [
            CMD_DATA, CMD_TXDELAY, CMD_PERSIST, CMD_SLOTTIME,
            CMD_TXTAIL, CMD_FULLDUP, CMD_HARDWARE, CMD_EXIT
        ]
        if cmd not in valid_cmds:
            raise ValueError(f"Invalid KISS command: 0x{cmd:02X}")

        try:
            frame = bytearray([FEND, cmd])
            for byte in payload:
                if byte == FEND:
                    frame.extend([FESC, TFEND])
                elif byte == FESC:
                    frame.extend([FESC, TFESC])
                else:
                    frame.append(byte)
            frame.append(FEND)

            self.serial.write(frame)
            logger.debug(f"Sent KISS frame: cmd=0x{cmd:02X}, len(payload)={len(payload)}")
        except serial.SerialException as e:
            logger.error(f"Serial write error: {e}")
            raise SerialError(f"Send failed: {e}")

    def _receive_loop(self):
        """Background thread: read bytes and process KISS frames."""
        while self._running:
            try:
                data = self.serial.read(1024)
                if not data:
                    continue
                for byte in data:
                    self._process_byte(byte)
            except serial.SerialException as e:
                logger.error(f"Serial read error: {e}")
                time.sleep(1)  # Backoff before retry
            except Exception as e:
                logger.exception(f"Unexpected receive error: {e}")
                break

    def _process_byte(self, byte: int):
        """Process incoming byte for KISS framing and destuffing."""
        if byte == FEND:
            if len(self.buffer) >= 1:  # At least command byte
                cmd = self.buffer[0]
                payload = self._destuff(self.buffer[1:])
                if self.on_frame:
                    self.on_frame(cmd, payload)
                else:
                    logger.debug(f"Received cmd=0x{cmd:02X}, len={len(payload)}")
            self.buffer = bytearray()
        else:
            self.buffer.append(byte)

    def _destuff(self, data: bytearray) -> bytes:
        """Remove KISS transparency escaping (FESC + TFEND/TFESC)."""
        destuffed = bytearray()
        i = 0
        while i < len(data):
            if data[i] == FESC:
                i += 1
                if i < len(data):
                    if data[i] == TFEND:
                        destuffed.append(FEND)
                    elif data[i] == TFESC:
                        destuffed.append(FESC)
                    else:
                        destuffed.append(data[i])
            else:
                destuffed.append(data[i])
            i += 1
        return bytes(destuffed)

    def set_param(self, cmd: int, value: int):
        """Convenience: send 1-byte parameter command."""
        self.send(bytes([value & 0xFF]), cmd)

    def close(self):
        """Graceful shutdown."""
        self._running = False
        if self.serial.is_open:
            self.serial.close()
        logger.info("KISS closed")

    def __del__(self):
        self.close()
