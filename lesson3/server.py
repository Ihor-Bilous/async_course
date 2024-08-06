import asyncio
import argparse
import json
import random
from datetime import datetime

parser = argparse.ArgumentParser(description="Weather server.")
parser.add_argument('--host', type=str, default="localhost")
parser.add_argument('--port', type=str, default=8000)


DEFAULT_PERIOD = 5
CLIENTS_STREAMS = {}
SEASONS = {
    1: "winter",
    2: "winter",
    3: "spring",
    4: "spring",
    5: "spring",
    6: "summer",
    7: "summer",
    8: "summer",
    9: "autumn",
    10: "autumn",
    11: "autumn",
    12: "winter",
}


def get_winter_weather_data() -> dict:
    return {
        "temperature_celsius": random.choice(list(range(-10, 6))),
        "humidity_percentage": random.choice(list(range(30, 40))),
        "wind_speed_kph": random.choice(list(range(8, 12))),
        "cloud_coverage_percentage": random.choice(list(range(50, 70))),
        "weather_condition": "Cloudy",
        "wind_direction": "S"
    }


def get_summer_weather_data() -> dict:
    return {
        "temperature_celsius": random.choice(list(range(20, 30))),
        "humidity_percentage": random.choice(list(range(30, 40))),
        "wind_speed_kph": random.choice(list(range(1, 3))),
        "cloud_coverage_percentage": random.choice(list(range(5, 15))),
        "weather_condition": "Sunny",
        "wind_direction": "N"
    }


def get_spring_weather_data() -> dict:
    return {
        "temperature_celsius": random.choice(list(range(10, 20))),
        "humidity_percentage": random.choice(list(range(50, 70))),
        "wind_speed_kph": random.choice(list(range(3, 5))),
        "cloud_coverage_percentage": random.choice(list(range(30, 40))),
        "weather_condition": "Sunny/Cloudy",
        "wind_direction": "E"
    }


def get_autumn_weather_data() -> dict:
    return {
        "temperature_celsius": random.choice(list(range(10, 20))),
        "humidity_percentage": random.choice(list(range(50, 70))),
        "wind_speed_kph": random.choice(list(range(3, 5))),
        "cloud_coverage_percentage": random.choice(list(range(30, 40))),
        "weather_condition": "Sunny/Cloudy",
        "wind_direction": "W"
    }


SEASONS_HANDLER = {
    "winter": get_winter_weather_data,
    "spring": get_spring_weather_data,
    "summer": get_summer_weather_data,
    "autumn": get_autumn_weather_data,
}


def generate_weather_data() -> dict:
    time = datetime.now()
    season = SEASONS[time.month]
    handler = SEASONS_HANDLER[season]
    return {
        "location": "Lviv",
        "pressure_hpa": 1000,
        "observation_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        **handler(),
    }


def register_client(
    addr: tuple[str, int],
    writer: asyncio.StreamWriter
) -> None:
    CLIENTS_STREAMS[addr] = writer
    print(f"Client {addr} was registered")


def unregister_client(addr: tuple[str, int]) -> None:
    CLIENTS_STREAMS.pop(addr, None)
    print(f"Client {addr} was unregistered")


async def close_connection(writer: asyncio.StreamWriter) -> None:
    writer.close()
    await writer.wait_closed()


async def close_connections():
    print("\nClosing clients connections...")
    close_sockets_tasks = []
    clients = CLIENTS_STREAMS.copy()

    for addr, writer in clients.items():
        if addr in CLIENTS_STREAMS:
            unregister_client(addr)
            close_sockets_tasks.append(asyncio.create_task(close_connection(writer)))
    await asyncio.gather(*close_sockets_tasks)


async def send_weather_data(
    addr: tuple[str, int],
    writer: asyncio.StreamWriter, data: bytes
) -> None:
    print(f"Sending weather data to {addr}")
    writer.write(data)
    await writer.drain()


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    addr = writer.get_extra_info("peername")
    register_client(addr, writer)

    # this is required to unregister client if client closed connection
    data = await reader.read(100)
    # if data is empty it means that client closed connection
    if not data:
        if addr in CLIENTS_STREAMS:
            unregister_client(addr)


async def send_periodic_weather_data(period: int = DEFAULT_PERIOD):
    while True:
        if CLIENTS_STREAMS:
            data = generate_weather_data()
            json_data = json.dumps(data, indent=4)
            encoded_data = json_data.encode()

            send_weather_tasks = []
            for addr, client_writer in CLIENTS_STREAMS.items():
                send_weather_tasks.append(
                    asyncio.create_task(send_weather_data(addr, client_writer, encoded_data))
                )
            await asyncio.gather(*send_weather_tasks)

        await asyncio.sleep(period)


async def main():
    args = parser.parse_args()
    print(f"Server starts: {args.host}:{args.port}")

    server = await asyncio.start_server(handle_client, args.host, args.port)
    async with server:
        try:
            run_time_tasks = [
                asyncio.create_task(server.serve_forever()),
                asyncio.create_task(send_periodic_weather_data())
            ]
            await asyncio.gather(*run_time_tasks)
        except (asyncio.CancelledError, KeyboardInterrupt):
            await close_connections()


if __name__ == "__main__":
    asyncio.run(main())
