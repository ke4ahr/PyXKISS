# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR

"""Entry point for running PyXKISS as a module (python -m pyxkiss).

Currently provides a simple CLI monitor/demo. Future: full CLI with subcommands.
"""

import argparse
import sys
import time
import logging
from pyxkiss.xkiss import XKISS

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("pyxkiss.cli")

def parse_args():
    parser = argparse.ArgumentParser(
        description="PyXKISS CLI - Simple KISS/XKISS/SMACK monitor and sender"
    )
    parser.add_argument(
        "--device", "-d", default="/dev/ttyUSB0",
        help="Serial device path (default: /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--baud", "-b", type=int, default=9600,
        help="Baud rate (default: 9600)"
    )
    parser.add_argument(
        "--address", "-a", type=int, default=0,
        help="Multi-drop TNC address (0-15, default: 0)"
    )
    parser.add_argument(
        "--polling", action="store_true",
        help="Enable active + passive polling mode"
    )
    parser.add_argument(
        "--poll-interval", type=float, default=0.1,
        help="Active poll interval in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--checksum", action="store_true",
        help="Enable optional XOR checksum mode"
    )
    parser.add_argument(
        "--max-queue", type=int, default=100,
        help="Max queued frames per port (default: 100)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if args.debug:
        logging.getLogger("pyxkiss").setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logger.info("Starting PyXKISS CLI monitor...")

    def on_frame(addr: int, port: int, payload: bytes):
        logger.info(f"RX addr={addr} port={port} len={len(payload)}: {payload.hex().upper()}")

    try:
        k = XKISS(
            device=args.device,
            baudrate=args.baud,
            address=args.address,
            polling_mode=args.polling,
            poll_interval=args.poll_interval,
            checksum_mode=args.checksum,
            max_queue_size=args.max_queue,
            on_frame=on_frame,
        )

        print(f"PyXKISS CLI running on {args.device} @ {args.baud} baud")
        print(f"Address: {args.address} | Polling: {'ON' if args.polling else 'OFF'} | "
              f"Checksum: {'ON' if args.checksum else 'OFF'} | Queue limit: {args.max_queue}")
        print("Press Ctrl+C to exit...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            k.close()

    except Exception as e:
        logger.critical(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
