#!/usr/bin/env python3
"""
Main entrypoint for the GossipApp.
Determines whether to run as client or server based on environment variables.
"""

import asyncio
import sys
import config
from client import main as client_main
from server import main as server_main


def main():
    """Main entrypoint that determines the application mode"""

    print("===  GossipApp   ===")
    print(f"Starting as {config.MODE.upper()}...")
    print(f"MODE: {config.MODE}")
    print(f"Coordinator address: {config.COORDINATOR_IP}:{config.COORDINATOR_PORT}")

    # Validate configuration
    if config.MODE not in ["server", "client"]:
        print("ERROR: Invalid MODE value")
        print("Please set MODE environment variable to one of:")
        print("  MODE=server  # to run as a server (coordinator)")
        print("  MODE=client  # to run as a client")
        sys.exit(1)

    # Run the appropriate mode
    if config.MODE == "server":
        print("Starting as COORDINATOR (server)...")
        print("Waiting for 2 clients to connect...")
        asyncio.run(server_main())
    elif config.MODE == "client":
        print("Starting as CLIENT...")
        asyncio.run(client_main())


if __name__ == "__main__":
    main()
