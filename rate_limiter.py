import time
from collections import defaultdict, deque
from threading import Lock

MAX_REQUESTS = 5
WINDOW_SECONDS = 60

requests = defaultdict(deque)
lock = Lock()


def is_allowed(hospital_id: str) -> bool:
    current_time = time.monotonic()

    with lock:
        timestamps = requests[hospital_id]

        # Remove requests older than 60 seconds
        while timestamps and current_time - timestamps[0] >= WINDOW_SECONDS:
            timestamps.popleft()

        # Check whether hospital exceeded its limit
        if len(timestamps) >= MAX_REQUESTS:
            return False

        # Record the current request
        timestamps.append(current_time)
        return True