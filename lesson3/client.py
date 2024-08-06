import asyncio
import argparse

parser = argparse.ArgumentParser(description="Weather cient.")
parser.add_argument('--host', type=str, default="localhost")
parser.add_argument('--port', type=str, default=8000)


async def tcp_echo_client():
    args = parser.parse_args()
    print(f"Client listening: {args.host}:{args.port}")

    reader, writer = await asyncio.open_connection(args.host, args.port)

    counter = 0
    try:

        while True:
            encoded_data = await reader.read(2048)
            # if data is empty it means that server closed connection
            if not encoded_data:
                print("Server closed the connection.")
                break
            decoded_data = encoded_data.decode()
            counter += 1
            print(f"{counter}: Weather data received:\n{decoded_data}\n")

    except (asyncio.CancelledError, KeyboardInterrupt):
        print('Connection is being closed.')
        writer.close()
        await writer.wait_closed()
        print("Connection was closed.")


async def main():
    await tcp_echo_client()


if __name__ == '__main__':
    asyncio.run(main())
