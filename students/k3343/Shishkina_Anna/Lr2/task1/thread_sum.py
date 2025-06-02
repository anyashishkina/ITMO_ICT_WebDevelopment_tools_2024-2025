import threading
import time

def partial_sum(start, end, results, index):
    results[index] = sum(range(start, end))

def calculate_sum_threading(n=100_000_000, num_threads=4):
    step = n // num_threads
    results = [0] * num_threads
    threads = []

    start_time = time.time()

    for i in range(num_threads):
        t = threading.Thread(target=partial_sum, args=(i * step + 1, (i + 1) * step + 1, results, i))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    total = sum(results)
    print(f"Threading result: {total}")
    print(f"Time: {time.time() - start_time:.2f} seconds\n")

calculate_sum_threading()
