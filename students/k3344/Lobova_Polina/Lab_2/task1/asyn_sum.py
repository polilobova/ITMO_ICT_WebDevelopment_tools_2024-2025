import asyncio
import time

"""
Async sum: 5000000050000000
Time: 8.3299 seconds
"""

async def calculate_chunk(start, end):
    """Асинхронное вычисление суммы для части диапазона"""
    total = 0
    for i in range(start, end + 1):
        total += i
        # Добавляем возможность переключения контекста
        if i % 1000 == 0:
            await asyncio.sleep(0)
    return total


async def calculate_sum(num_tasks=4):
    n = 100000000
    chunk_size = n // num_tasks
    tasks = []

    start_time = time.time()

    # Создаем задачи
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else n
        task = asyncio.create_task(calculate_chunk(start, end))
        tasks.append(task)

    # Ждем завершения всех задач
    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Async sum: {total_sum}")
    print(f"Time: {end_time - start_time:.4f} seconds")
    return total_sum


if __name__ == "__main__":
    asyncio.run(calculate_sum())