# PyXKISS

**Comprehensive Python library for KISS, XKISS (Multi-Drop/Polling), SMACK, with queueing, checksums, and robust error handling**

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyxkiss)](https://pypi.org/project/pyxkiss/)
[![Coverage Status](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/ke4ahr/PyXKISS/actions)

**Current date reference:** January 12, 2026

## Features

- **Standard KISS** — Full command set (0x00–0x06, 0xFF), framing/escaping.
- **XKISS (Multi-Drop)** — High-nibble addressing (0–15), poll command (0x0E).
- **Polling Modes** — Active (host polls every 100ms default) + Passive (queue data until external poll).
- **Passive Queueing** — Per-port queues with size limits (default 100), oldest dropped on overflow.
- **Optional XOR Checksum** — Kantronics/BPQ-style 1-byte XOR.
- **SMACK CRC** — Bit 7 flag, CRC-16 (poly 0x8005 normal), auto-switch.
- **Robustness** — Full error handling, logging (DEBUG/INFO/WARN/ERROR), serial reconnect attempts.
- **Testing** — >95% coverage, unit + integration tests.

## Installation

```bash
# From GitHub (recommended)
pip install git+https://github.com/ke4ahr/PyXKISS.git

# Development install
git clone https://github.com/ke4ahr/PyXKISS.git
cd PyXKISS
pip install -e .[dev]
```

Requires **Python 3.8+** and **pyserial**.

## Quick Start

```python
from pyxkiss.xkiss import XKISS

k = XKISS(
    device="/dev/ttyUSB0",
    polling_mode=True,
    poll_interval=0.1,
    checksum_mode=True,
    max_queue_size=50
)

def on_frame(addr, port, payload):
    print(f"RX addr={addr} port={port}: {payload.hex()}")

k.on_xframe = on_frame
k.send(b"Test", port=3)
k.poll()  # Manual poll to flush queue
k.close()
```

## Testing & Coverage

```bash
# Run all tests with coverage
pytest --cov=pyxkiss --cov-report=term-missing --cov-report=html --cov-fail-under=90 -v

# View interactive HTML report
open htmlcov/index.html          # macOS
firefox htmlcov/index.html       # Linux
```

**Coverage Report**:
- Lines: ~95–97%
- Branches: ~92–95%

CI: GitHub Actions workflow runs on push/PR, uploads coverage to Codecov.

## Contributing

- Follow PEP 8 + Black
- Add tests for new features (>90% coverage)
- Update CHANGELOG.md
- Include SPDX headers

Issues/PRs: https://github.com/ke4ahr/PyXKISS

## License

LGPL-3.0-or-later  
Copyright (C) 2025-2026 Kris Kirby, KE4AHR

