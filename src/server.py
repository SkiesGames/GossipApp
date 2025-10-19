import asyncio
import config
from telegram_interactions import send_notification


class Coordinator:
    def __init__(self):
        self.client_messages = {}  # Store client address -> message mapping
        self.expected_clients = 2  # We expect 2 clients
        self.message_sent = False  # Flag to track if message was already sent

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        client_id = f"{addr[0]}:{addr[1]}"

        try:
            # Read message length (4 bytes)
            length_data = await reader.readexactly(4)
            message_length = int.from_bytes(length_data, byteorder="big")
            print(f"Expected message length: {message_length} bytes from {client_id}")

            # Read the exact message length
            data = await reader.readexactly(message_length)
            message = data.decode()
            print(f"Received {message!r} from {client_id}")

            # Store the message for this client
            self.client_messages[client_id] = message
            print(f"Stored message from {client_id}: {message}")
            print(f"Current clients: {list(self.client_messages.keys())}")

            # Check if we have messages from all expected clients and haven't sent yet
            if (
                len(self.client_messages) >= self.expected_clients
                and not self.message_sent
            ):
                await self.send_combined_message()

            # Send acknowledgment
            response = "Message received"
            response_bytes = response.encode()
            response_length = len(response_bytes)

            # Send length first (4 bytes)
            length_prefix = response_length.to_bytes(4, byteorder="big")
            writer.write(length_prefix)
            await writer.drain()

            # Send the actual response
            writer.write(response_bytes)
            await writer.drain()

            print(f"Sent acknowledgment to {client_id}")

        except Exception as e:
            print(f"Error handling connection from {client_id}: {e}")
        finally:
            print(f"Closing connection with {client_id}")
            writer.close()
            await writer.wait_closed()

    async def send_combined_message(self):
        """Combine messages from all clients and send via Telegram"""
        if len(self.client_messages) < self.expected_clients:
            print(
                f"Not enough messages yet. Have {len(self.client_messages)}, need {self.expected_clients}"
            )
            return

        if self.message_sent:
            print("Message already sent for this round, skipping")
            return

        # Combine messages in order of client connection
        combined_message = " ".join(self.client_messages.values())
        print(f"Combined message: {combined_message}")

        # Send via Telegram
        if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
            success = send_notification(combined_message)
            if success:
                print("Message sent to Telegram successfully!")
                self.message_sent = True  # Mark as sent
            else:
                print("Failed to send message to Telegram")
        else:
            print("Telegram credentials not configured, skipping notification")
            self.message_sent = True  # Mark as sent even if no Telegram

        # Clear messages after sending
        self.client_messages.clear()
        print("Cleared client messages")


async def main():
    coordinator = Coordinator()
    server = await asyncio.start_server(
        coordinator.handle_client, "0.0.0.0", config.COORDINATOR_PORT
    )

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Coordinator serving on {addrs}")
    print(f"Waiting for {coordinator.expected_clients} clients...")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
