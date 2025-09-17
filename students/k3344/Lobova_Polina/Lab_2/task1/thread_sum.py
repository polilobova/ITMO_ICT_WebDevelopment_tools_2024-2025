import threading
import time

"""Результат:

Threading sum: 5000000050000000
Time: 4.1727 seconds

"""

def calculate_chunk(start, end, result, index):
    """Вычисление суммы для части диапазона"""
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def calculate_sum(num_threads=4):
    n = 100000000
    chunk_size = n // num_threads
    threads = []
    result = [0] * num_threads

    start_time = time.time()

    # Создаем и запускаем потоки
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else n
        thread = threading.Thread(
            target=calculate_chunk,
            args=(start, end, result, i)
        )
        threads.append(thread)
        thread.start()

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()

    # Суммируем результаты
    total_sum = sum(result)
    end_time = time.time()

    print(f"Threading sum: {total_sum}")
    print(f"Time: {end_time - start_time:.4f} seconds")
    return total_sum


if __name__ == "__main__":
    calculate_sum()