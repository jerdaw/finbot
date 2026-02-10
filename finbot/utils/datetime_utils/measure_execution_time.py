import time


def measure_execution_time(func):
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    return end_time - start_time
