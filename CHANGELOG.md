# PyXKISS Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-09

### Added
- Full standard KISS implementation (framing, escaping, commands)
- Extended KISS (XKISS/multi-drop): high-nibble addressing, poll 0x0E
- Active polling (host-initiated periodic polls)
- Passive polling + queueing: per-port deques, max size limit (default 100)
- Optional 1-byte XOR checksum (Kantronics/BPQ style)
- SMACK CRC extension (poly 0x8005 normal, auto-switch)
- Comprehensive error handling (custom exceptions, serial reconnect attempt)
- Detailed logging (DEBUG/INFO/WARN/ERROR)
- >95% test coverage (unit + integration)
- Modern packaging (pyproject.toml, PEP 621)
- CLI entry point (`python -m pyxkiss`)

### Changed
- Renamed "polled mode" to "polling mode"
- Default active poll interval = 100 ms
- Added passive queueing with external poll response

### Fixed
- Graceful shutdown and thread cleanup
- Input validation (address, interval, queue size)

### Removed
- None (initial release)

## [Unreleased]

- Planned: AGWPE TCP/IP bridge
- Planned: 0xC command frame ID/ack support
- Planned: Automatic persistent reconnect loop
