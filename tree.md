pyxkiss/
├── __init__.py                # Package init + version
├── constants.py               # All protocol constants
├── kiss.py                    # Base KISS class
├── xkiss.py                   # Extended KISS (multi-drop, polling active/passive, queueing + limits, checksum)
├── smack.py                   # SMACK CRC layer (inherits from XKISS)
├── interface.py               # Shared serial base
├── exceptions.py              # Custom exceptions
├── __main__.py                # Optional CLI entry (e.g., python -m pyxkiss)
├── tests/
│   ├── __init__.py
│   ├── test_kiss.py
│   ├── test_xkiss.py
│   ├── test_smack.py
│   └── test_integration.py    # Full end-to-end tests
├── pyproject.toml             # Build config (below)
├── README.md                  # Updated below
├── LICENSE                    # LGPL-3.0-or-later
├── CHANGELOG.md               # Version history
└── setup.cfg                  # Optional legacy config
