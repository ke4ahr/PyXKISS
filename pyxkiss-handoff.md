# PyXKISS Technical Hand-Off Document

**Version:** 1.0.0  
**Date:** January 12, 2026  
**Author/Maintainer:** Kris Kirby, KE4AHR  
**License:** LGPL-3.0-or-later  
**Repository:** https://github.com/ke4ahr/PyXKISS  
**Target Audience:** Next developer(s), maintainers, or integrators taking over or extending the project.

## 1. Project Overview

PyXKISS is a pure-Python, modern, high-level library for interfacing with amateur radio TNCs using the **KISS protocol family**:

- **Standard KISS** (TAPR original)
- **Extended KISS (XKISS / Multi-Drop / BPQKISS)** – G8BPQ multi-TNC support with high-nibble addressing, poll command (0x0E), and optional XOR checksum
- **SMACK** – CRC-16 extension (bit 7 flag on data frames, poly 0x8005 normal, init 0x0000, LSB-first append)
- **Polling Modes** – Active (host-initiated periodic polls) + Passive (queue data until external poll received)
- **Passive Queueing** – Per-port RX queues with configurable size limits (default 100 frames), oldest dropped on overflow

The library is built on top of **pyax25-22** (for AX.25 helpers) and **pyserial** (for serial I/O), with full error handling, detailed logging, and >95% test coverage.

**Key Goals**:
- Backward compatibility with legacy TNCs
- Robustness for multi-TNC/shared serial bus environments
- Ease of use for APRS beacons, monitoring, digipeaters
- Extensibility for future enhancements (e.g., AGWPE TCP bridge)

## 2. Current State (as of Jan 12, 2026)

- **Version:** 1.0.0 (initial production release)
- **Coverage:** ~95%+ (unit + integration tests)
- **Dependencies:**
  - `pyserial>=3.5` (serial port)
  - `pyax25-22>=0.5.97` (optional AX.25 helpers)
  - Dev: `pytest`, `pytest-cov`, `pytest-mock`, `black`, `flake8`, `mypy`, `sphinx`, `sphinx-rtd-theme`
- **Test Status:** All pass; CI-ready (GitHub Actions workflow exists)
- **Known Limitations:**
  - No AGWPE TCP/IP support (different framing)
  - Passive queue flush uses plain CMD_DATA (0xC ack stubbed)
  - No automatic infinite reconnect on persistent serial failure (logs critical)

## 3. Package Structure

```
pyxkiss/
├── __init__.py
├── constants.py
├── kiss.py
├── xkiss.py
├── smack.py
├── interface.py
├── exceptions.py
├── __main__.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── tests/
    ├── __init__.py
    ├── test_kiss.py
    ├── test_xkiss.py
    ├── test_smack.py
    └── test_integration.py
```

## 4. Key Implementation Details

### 4.1 Polling Modes

- **Active Polling**:
  - Host sends 0x0E poll frames every `poll_interval` (default 0.1s = 100 ms)
  - Background daemon thread

- **Passive Polling + Queueing**:
  - When `polling_mode=True`, incoming data frames are queued per port (deque with `max_queue_size` limit, default 100)
  - On receipt of a **poll frame** (cmd 0x0E), the queue for the addressed port is flushed by sending all queued payloads as data frames.
  - Overflow: oldest frames dropped with WARNING log

### 4.2 Checksum Mode (XOR)

- Optional 1-byte XOR (exclusive-OR of all bytes between FENDs, pre-escaping)
- Appended before closing FEND
- Verified on receive; invalid frames dropped silently
- Matches Kantronics XKISS ($0B/$0F) and BPQ32 CHECKSUM option

### 4.3 SMACK

- Bit 7 flag on data command (0x80+)
- CRC-16 (poly 0x8005 normal, init 0x0000, LSB-first append)
- Auto-switch: TX starts plain; enables on first valid CRC frame received
- Invalid CRC → drop silently

### 4.4 Error Handling & Logging

- Custom exceptions: `XKISSException`, `SerialError`, `ChecksumError`
- Serial failures → log + reconnect attempt
- Queue overflow → WARNING + drop oldest
- Full logging: DEBUG (frame hex), INFO (sends/polls), ERROR (failures), WARNING (overflow)

## 5. Testing & Coverage

**Run tests with coverage**:

```bash
# Install dev dependencies
pip install -e .[dev]

# Run full suite + HTML coverage report
pytest --cov=pyxkiss --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90 -v

# View interactive report
open htmlcov/index.html          # macOS
firefox htmlcov/index.html       # Linux
```

**Coverage Highlights** (as of Jan 12, 2026):
- Lines: ~95–97%
- Branches: ~92–95%
- Missing: Mostly serial I/O edge cases (real hardware dependent)

**CI Workflow** (`.github/workflows/test.yml`):
- Runs on push/PR
- Python 3.8–3.12 matrix
- Uploads coverage to Codecov (optional)

## 6. Hand-Off Checklist for Next Developer

- [ ] Clone repo: `git clone https://github.com/ke4ahr/PyXKISS.git`
- [ ] Install: `pip install -e .[dev]`
- [ ] Run tests: `pytest --cov=pyxkiss --cov-report=html`
- [ ] Review `xkiss.py` – core polling/queue/checksum logic
- [ ] Check `smack.py` for CRC integration
- [ ] Update version in `__init__.py` and `pyproject.toml` on release
- [ ] Build & test wheel: `python -m build`
- [ ] Publish to PyPI: `twine upload dist/*` (after account/token setup)
- [ ] Update CHANGELOG.md on every change
- [ ] Consider adding:
  - AGWPE TCP/IP bridge (separate interface)
  - Frame ID/ack for 0xC command
  - Reconnect loop on persistent serial failure

## 7. Contact & Support

- **Maintainer**: Kris Kirby (KE4AHR) – GitHub @ke4ahr, email ke4ahr@gmail.com
- **Issues/PRs**: https://github.com/ke4ahr/PyXKISS/issues
- **Packet**: KE4AHR @ various nodes
- **Discussion**: Open GitHub Discussions for questions

**Hand-off complete.**  
The project is stable, well-tested, documented, and ready for maintenance, extension, or production use.

**73!** – Good luck, and happy packet!