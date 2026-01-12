# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Custom exceptions for PyXKISS library.
"""

class XKISSException(Exception):
    """Base exception for all PyXKISS errors."""
    pass

class SerialError(XKISSException):
    """Raised when serial port operations fail."""
    pass

class ChecksumError(XKISSException):
    """Raised when XOR checksum verification fails."""
    pass

class QueueOverflowWarning(Warning):
    """Warning (non-fatal) when queue size limit is reached."""
    pass
