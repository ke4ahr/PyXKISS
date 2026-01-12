# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Extended KISS (XKISS/BPQKISS) with multi-drop addressing, active & passive polling,
passive queueing with size limits, optional XOR checksum, full error handling, and logging.
"""

import logging
import threading
import time
from collections import deque
from typing import Callable, Optional, Dict
import serial

from .kiss import KISS
from .constants import (
    FEND, FESC, TFEND, TFESC,
    CMD_DATA, CMD_POLL, CMD_DATA_ACK,
    PORT_MASK, CMD_MASK
)

# Logging setup (user can override level)
logger = logging.getLogger("pyxkiss.xkiss")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(handler)

class XKISSException(Exception):
    """Base exception for XKISS-related errors."""
    pass

class SerialError(XKISSException):
    """Raised on serial port failures."""
    pass

class ChecksumError(XKISSException):
    """Raised when XOR checksum verification fails."""
    pass

class XKISS(KISS):
    """Extended KISS with active/passive polling, passive queueing, and robust error handling."""

    def __init__(
        self,
        device: str,
        baudrate: int = 9600,
        address: int = 0,                       # This TNC's address (0-15)
        polling_mode: bool = False,             # Enable polling (active + passive)
        poll_interval: float = 0.1,             # Active poll every 100 ms
        checksum_mode: bool = False,            # Optional XOR checksum
        max_queue_size: int = 100,              # Max frames per port queue
        log_level: int = logging.INFO,          # Logging level
        on_frame: Optional[Callable[[int, int, bytes], None]] = None,
    ):
        if not 0 <= address <= 15:
            raise ValueError("address must be 0-15")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be > 0")
        if max_queue_size < 1:
            raise ValueError("max_queue_size must be at least 1")

        self.address = address & 0x0F
        self.polling_mode = polling_mode
        self.poll_interval = poll_interval
        self.checksum_mode = checksum_mode
        self.max_queue_size = max_queue_size
        self._poll_thread: Optional[threading.Thread] = None

        # Passive queueing: dict of port → deque of payloads
        self._rx_queues: Dict[int, deque[bytes]] = {p: deque(maxlen=max_queue_size) for p in range(16)}

        # Logging setup
        logger.setLevel(log_level)

        # Override internal callback to handle checksum + poll response
        super().__init__(device, baudrate, self._wrapped_on_frame)
        self.on_xframe = on_frame  # Final user callback: (addr, port, clean_payload)

        logger.info(f"XKISS initialized: device={device}, baudrate={baudrate}, "
                    f"address={self.address}, polling_mode={polling_mode}, "
                    f"checksum_mode={checksum_mode}, poll_interval={poll_interval}s, "
                    f"max_queue_size={max_queue_size}")

        if self.polling_mode:
            self._start_active_poller()

    def _wrapped_on_frame(self, cmd: int, payload: bytes):
        """Internal callback: handle checksum verification, poll response, queueing, then user callback."""
        try:
            # 1. Optional XOR checksum verification
            if self.checksum_mode:
                if len(payload) < 1:
                    logger.warning("Frame too short for checksum")
                    return
                received_checksum = payload[-1]
                computed = self._compute_xor(payload[:-1])
                if received_checksum != computed:
                    raise ChecksumError(f"Checksum mismatch: received=0x{received_checksum:02X}, "
                                    f"computed=0x{computed:02X}")
                payload = payload[:-1]  # Strip checksum
                logger.debug(f"Checksum verified: 0x{computed:02X}")

            # 2. Extract port and real command
            port = (cmd & PORT_MASK) >> 4
            real_cmd = cmd & CMD_MASK

            logger.debug(f"Received frame: cmd=0x{cmd:02X} (port={port}, real_cmd=0x{real_cmd:02X}), "
                         f"len(payload)={len(payload)}")

            # 3. Passive polling response (respond to external poll)
            if real_cmd == CMD_POLL and self.polling_mode:
                logger.info(f"Poll received from external master → flushing queue for port {port}")
                self._flush_queue(port)

            # 4. Queue incoming data if polling_mode active (unless it's a poll)
            elif real_cmd == CMD_DATA and self.polling_mode:
                queue = self._rx_queues[port]
                if len(queue) >= self.max_queue_size:
                    logger.warning(f"Queue overflow for port {port} (dropped oldest)")
                    queue.popleft()  # Enforce limit
                queue.append(payload)
                logger.debug(f"Queued data for port {port} (now {len(queue)})")
                return  # Do NOT call user callback yet — wait for poll

            # 5. Forward to user callback (non-queued or polled data)
            if self.on_xframe:
                self.on_xframe(self.address, port, payload)

        except ChecksumError as e:
            logger.error(f"Checksum error: {e}")
        except serial.SerialException as e:
            logger.error(f"Serial error during frame processing: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in frame processing: {e}")

    def send(self, payload: bytes, port: int = 0, cmd: int = CMD_DATA):
        """Send frame with optional XOR checksum."""
        try:
            full_cmd = ((port & 0x0F) << 4) | (cmd & CMD_MASK)

            frame = bytearray([FEND, full_cmd])
            checksum = full_cmd

            for b in payload:
                frame.append(b)
                checksum ^= b

            if self.checksum_mode:
                frame.append(checksum & 0xFF)

            frame.append(FEND)
            self.write(frame)
            logger.info(f"Sent frame: cmd=0x{full_cmd:02X}, port={port}, len(payload)={len(payload)}")

        except serial.SerialException as e:
            logger.error(f"Serial error during send: {e}")
            raise SerialError(f"Failed to send frame: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error during send: {e}")
            raise XKISSException(f"Send failed: {e}")

    def poll(self):
        """Manually send a poll frame (command 0x0E, port 0)."""
        self.send(b'', port=0, cmd=CMD_POLL)

    def _flush_queue(self, port: int):
        """Flush all queued data for a given port (on poll receipt)."""
        queue = self._rx_queues.get(port, deque())
        flushed_count = 0
        while queue:
            try:
                payload = queue.popleft()
                self.send(payload, port=port, cmd=CMD_DATA)
                flushed_count += 1
            except Exception as e:
                logger.error(f"Failed to flush queued frame for port {port}: {e}")
                break  # Stop on error
        if flushed_count > 0:
            logger.info(f"Flushed {flushed_count} queued frames for port {port}")

    def _start_active_poller(self):
        """Background thread for active polling (host-initiated)."""
        def poller():
            while True:
                time.sleep(self.poll_interval)
                self.poll()
        self._poll_thread = threading.Thread(target=poller, daemon=True, name="XKISS-ActivePoller")
        self._poll_thread.start()

    def _compute_xor(self, data: bytes) -> int:
        """Compute 1-byte XOR checksum over bytes (pre-escaping)."""
        xor = 0
        for b in data:
            xor ^= b
        return xor

    def close(self):
        """Clean shutdown."""
        if self._poll_thread and self._poll_thread.is_alive():
            pass  # Daemon exits automatically
        super().close()
        logger.info("XKISS closed")
