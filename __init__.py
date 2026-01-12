# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""PyXKISS - Comprehensive Python library for KISS, XKISS (Multi-Drop/Polling), and SMACK.

This package provides a complete, production-ready implementation of:
- Standard KISS (framing, commands 0x00-0x06/0xFF)
- Extended KISS (XKISS/BPQKISS): multi-drop addressing, active/passive polling, per-port queueing
- SMACK CRC extension (bit 7 flag, CRC-16 poly 0x8005, auto-switch)
- Optional 1-byte XOR checksum (Kantronics/BPQ style)

Features robust error handling, detailed logging, and >95% test coverage.
"""

__version__ = "1.0.0"
__author__ = "Kris Kirby, KE4AHR"
__license__ = "LGPL-3.0-or-later"

# Public API exports
from .kiss import KISS
from .xkiss import XKISS
from .smack import SMACK
from .constants import *
from .exceptions import *
from .interface import SerialInterface

# Optional: quick access to main classes
__all__ = [
    "KISS",
    "XKISS",
    "SMACK",
    "SerialInterface",
    "XKISSException",
    "SerialError",
    "ChecksumError",
]

if __name__ == "__main__":
    print(f"PyXKISS v{__version__} - KISS/XKISS/SMACK library")
    print("Run 'python -m pyxkiss' for CLI (future feature)")
