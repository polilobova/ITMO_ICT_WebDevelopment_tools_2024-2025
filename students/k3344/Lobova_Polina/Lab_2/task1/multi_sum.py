import multiprocessing
import time

"""
Multiprocessing sum: 5000000050000000
Time: 1.3054 seconds

"""

def calculate_chunk(start, end, result, index):
    """Вычисление суммы для части диапазона"""
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def calculate_sum(num_processes=4):
    n = 100000000
    chunk_size = n // num_processes
    processes = []

    # Используем Manager для разделяемой памяти
    with multiprocessing.Manager() as manager:
        result = manager.list([0] * num_processes)

        start_time = time.time()

        # Создаем и запускаем процессы
        for i in range(num_processes):
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size if i != num_processes - 1 else n
            process = multiprocessing.Process(
                target=calculate_chunk,
                args=(start, end, result, i)
            )
            processes.append(process)
            process.start()

        # Ждем завершения всех процессов
        for process in processes:
            process.join()

        # Суммируем результаты
        total_sum = sum(result)
        end_time = time.time()

        print(f"Multiprocessing sum: {total_sum}")
        print(f"Time: {end_time - start_time:.4f} seconds")
        return total_sum


if __name__ == "__main__":
    calculate_sum()