from multiprocessing import Process, Manager
import time

def partial_sum(start, end, results, index):
    results[index] = sum(range(start, end))

def calculate_sum_multiprocessing(n=10_00_000_000, num_processes=4):
    step = n // num_processes
    manager = Manager()
    results = manager.list([0] * num_processes)
    processes = []

    start_time = time.time()

    for i in range(num_processes):
        p = Process(target=partial_sum, args=(i * step + 1, (i + 1) * step + 1, results, i))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    total = sum(results)
    print(f"Multiprocessing result: {total}")
    print(f"Time: {time.time() - start_time:.2f} seconds\n")

if __name__ == '__main__':
    calculate_sum_multiprocessing()
