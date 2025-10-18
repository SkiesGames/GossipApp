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
    
    print("=== GossipApp ===")
    print(f"IS_CLIENT: {config.IS_CLIENT}")
    print(f"IS_SERVER: {config.IS_SERVER}")
    print(f"Coordinator address: {config.coordinator_address}")
    
    # Validate configuration
    if not config.IS_CLIENT and not config.IS_SERVER:
        print("ERROR: Neither IS_CLIENT nor IS_SERVER is set to true")
        print("Please set one of the following environment variables:")
        print("  IS_CLIENT=true  # to run as a client")
        print("  IS_SERVER=true  # to run as a server (coordinator)")
        sys.exit(1)
    
    if config.IS_CLIENT and config.IS_SERVER:
        print("ERROR: Both IS_CLIENT and IS_SERVER are set to true")
        print("Please set only one of them to true")
        sys.exit(1)
    
    # Run the appropriate mode
    if config.IS_SERVER:
        print("Starting as COORDINATOR (server)...")
        print("Waiting for 2 clients to connect...")
        asyncio.run(server_main())
    elif config.IS_CLIENT:
        print("Starting as CLIENT...")
        asyncio.run(client_main())

if __name__ == "__main__":
    main()
