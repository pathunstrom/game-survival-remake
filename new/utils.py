from functools import wraps
from time import perf_counter


def debounce(wait_time):
    last_call = 0

    def outer_wrapper(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            nonlocal last_call
            now = perf_counter()
            if now - last_call >= wait_time:
                last_call = now
                return function(*args, **kwargs)

        return decorator
    return outer_wrapper
