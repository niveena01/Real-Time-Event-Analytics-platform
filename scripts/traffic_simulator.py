import asyncio
import aiohttp
import random
import time
import argparse

FASTAPI_URL = "http://localhost:8000/api/v1/events"

async def send_event(session):
    event_types = ["page_view", "click", "add_to_cart", "checkout", "error_500"]
    weights = [0.5, 0.3, 0.1, 0.07, 0.03]
    
    payload = {
        "client_id": f"app_client_{random.randint(1, 10)}",
        "event_type": random.choices(event_types, weights=weights)[0],
        "latency_ms": random.randint(10, 450),
        "user_id": f"usr_{random.randint(1000, 9999)}"
    }
    try:
        async with session.post(FASTAPI_URL, json=payload) as resp:
            await resp.read()
    except Exception:
        pass

async def main(rate, duration):
    print(f"Starting traffic generator: {rate} req/sec for {duration} seconds...")
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        start_time = time.time()
        while time.time() - start_time < duration:
            batch_start = time.time()
            tasks = [send_event(session) for _ in range(rate)]
            await asyncio.gather(*tasks)
            elapsed = time.time() - batch_start
            sleep_time = max(0, 1.0 - elapsed)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=int, default=1000, help="Events per second")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    args = parser.parse_args()
    asyncio.run(main(args.rate, args.duration))