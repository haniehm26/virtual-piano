import time 
import psutil


def monitor_cpu_usage(last_time, interval=1):
    """
    Measures CPU usage asynchronously at fixed intervals.
    :param last_time: Timestamp of the last measurement.
    :param interval: Time interval (seconds) between measurements.
    :return: CPU usage (or None if not enough time has passed).
    """
    current_time = time.time()
    if current_time - last_time >= interval:  # check if enough time has passed
        cpu_usage = psutil.cpu_percent(interval=0)
        return cpu_usage, current_time
    return None, last_time


def smooth_cpu_usage(cpu_usage, history, max_history=5):
    """
    Smooths the CPU usage using a moving average.
    :param cpu_usage: The latest CPU usage value.
    :param history: A deque containing the history of CPU usage values.
    :param max_history: Maximum number of historical values to keep.
    :return: Smoothed CPU usage.
    """
    if cpu_usage is not None:
        history.append(cpu_usage)
        if len(history) > max_history:
            history.popleft()  # remove the oldest value if history exceeds max size

    # calculate the average of the history
    smoothed_usage = sum(history) / len(history) if history else 0
    return smoothed_usage

def calculate_fps(frame_count, start_time):
    elapsed_time = time.time() - start_time
    return frame_count / elapsed_time if elapsed_time > 0 else 0