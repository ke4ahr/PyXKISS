# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Shared constants for KISS, XKISS (multi-drop), SMACK, and XOR checksum modes.

References:
- Standard KISS: TAPR spec
- XKISS/Multi-Drop: G8BPQ / Karl Medcalf WK5M documentation
- SMACK: Stuttgart Modified Amateur radio CRC-KISS (SYMEK)
"""

# Frame delimiters (shared across all modes)
FEND = 0xC0
FESC = 0xDB
TFEND = 0xDC
TFESC = 0xDD

# Standard KISS commands (low nibble)
CMD_DATA        = 0x00  # Data frame
CMD_TXDELAY     = 0x01  # Set TX Delay
CMD_PERSIST     = 0x02  # Set P-Persistence
CMD_SLOTTIME    = 0x03  # Set Slot Time
CMD_TXTAIL      = 0x04  # Set TX Tail
CMD_FULLDUP     = 0x05  # Set Full Duplex
CMD_HARDWARE    = 0x06  # Set Hardware (vendor-specific)
CMD_EXIT        = 0xFF  # Exit KISS mode

# XKISS / Multi-Drop / BPQKISS extensions
CMD_POLL        = 0x0E  # Poll command (requests queued data)
CMD_DATA_ACK    = 0x0C  # Extended data (with frame ID/ack - stubbed)

# SMACK CRC flags and parameters
SMACK_FLAG      = 0x80  # Bit 7 set on data command for CRC
SMACK_POLY      = 0x8005  # CRC-16 polynomial (normal/non-reflected)
SMACK_INIT      = 0x0000  # Initial CRC value
SMACK_CRC_SIZE  = 2     # 2 bytes appended LSB-first

# Masks
PORT_MASK       = 0xF0  # High nibble = port/address (0-15)
CMD_MASK        = 0x0F  # Low nibble = command type

# Other defaults
DEFAULT_BAUDRATE    = 9600
DEFAULT_POLL_INTERVAL = 0.1   # 100 ms
DEFAULT_MAX_QUEUE   = 100     # frames per port

# Vendor-specific / optional modes
CHECKSUM_FLAG   = 0x01  # Bit flag for optional XOR checksum mode (not in spec)
