import asyncio
import time
import random

import config

class ReliableTCPClient:
    def __init__(self, host, port, timeout=3, reconnect_delay=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reconnect_delay = reconnect_delay
        self.reader = None
        self.writer = None
        self.connected = False
        
    async def connect(self):
        """Establish connection with timeout and retry logic"""
        while True:
            try:
                print(f"Attempting to connect to {self.host}:{self.port}...")
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=self.timeout
                )
                self.connected = True
                print(f"Successfully connected to {self.host}:{self.port}")
                return True
                
            except asyncio.TimeoutError:
                print(f"Connection timeout after {self.timeout}s")
            except Exception as e:
                print(f"Connection failed: {e}")
                
            print(f"Retrying in {self.reconnect_delay} seconds...")
            await asyncio.sleep(self.reconnect_delay)
    
    async def send_message(self, message):
        """Send a message with length prefix"""
        if not self.connected or self.writer is None:
            raise ConnectionError("Not connected to server")
            
        try:
            message_bytes = message.encode()
            message_length = len(message_bytes)
            
            # Send length prefix (4 bytes, big-endian)
            length_prefix = message_length.to_bytes(4, byteorder='big')
            self.writer.write(length_prefix)
            await self.writer.drain()
            
            # Send the actual message
            self.writer.write(message_bytes)
            await self.writer.drain()
            
            print(f'Sent: {message!r} (length: {message_length} bytes)')
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            return False
    
    async def receive_message(self):
        """Receive a message with length prefix"""
        if not self.connected or self.reader is None:
            raise ConnectionError("Not connected to server")
            
        try:
            # Read message length (4 bytes)
            length_data = await self.reader.readexactly(4)
            message_length = int.from_bytes(length_data, byteorder='big')
            print(f"Expected response length: {message_length} bytes")
            
            # Read the exact message length
            data = await self.reader.readexactly(message_length)
                
            response = data.decode()
            print(f'Received: {response!r}')
            return response
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            self.connected = False
            raise
    
    async def close(self):
        """Close the connection"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        print("Connection closed")
    
    async def is_connected(self):
        """Check if connection is still alive"""
        return self.connected and self.writer is not None and not self.writer.is_closing()

async def main():
    client = ReliableTCPClient(config.COORDINATOR_IP, config.COORDINATOR_PORT)
    
    # Random words for the client to send
    random_words = [
        "Hello", "World", "Python", "Async", "Network", "Message", 
        "Client", "Server", "Coordinator", "Telegram", "Bot", "API",
        "Connection", "Socket", "Protocol", "Data", "Stream", "Buffer"
    ]
    
    try:
        # Connect with automatic retry
        await client.connect()
        
        # Generate and send a random message
        random_message = random.choice(random_words)
        print(f"Client sending random message: {random_message}")
        
        # Send the message
        success = await client.send_message(random_message)
        if success:
            response = await client.receive_message()
            print(f"Server response: {response}")
            print("Message sent successfully!")
        else:
            print("Failed to send message")
        
    except KeyboardInterrupt:
        print("Client interrupted by user")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())