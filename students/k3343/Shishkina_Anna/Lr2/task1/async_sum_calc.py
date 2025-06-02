import asyncio
import time

async def partial_sum(start, end):
    return sum(range(start, end))

async def calculate_sum_async(n=100_000_000, num_tasks=4):
    step = n // num_tasks
    tasks = []
    start_time = time.time()

    for i in range(num_tasks):
        tasks.append(asyncio.create_task(partial_sum(i * step + 1, (i + 1) * step + 1)))

    results = await asyncio.gather(*tasks)
    total = sum(results)

    print(f"Async result: {total}")
    print(f"Time: {time.time() - start_time:.2f} seconds\n")

asyncio.run(calculate_sum_async())
