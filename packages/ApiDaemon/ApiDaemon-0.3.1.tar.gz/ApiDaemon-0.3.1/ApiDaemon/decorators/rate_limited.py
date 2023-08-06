import time
from functools import wraps
import asyncio


class RateLimited:
    def __init__ (self, max_per_second):
        self.lock = asyncio.Lock()
        self.calls = 0
        self.last_call = 0
        self.max_calls = max_per_second

    def inc_calls(self):
        if time.time() != self.last_call:
            self.calls = 0
        self.calls += 1

    def wait(self):
        if self.calls >= self.max_calls:
            while int(time.time()) == self.last_call:
                yield from asyncio.sleep(0.01)
        self.inc_calls()

    def __call__(self, func):
        @asyncio.coroutine
        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            with (yield from self.lock):
                self.wait()
                return (yield from func(*args, **kwargs))

        return rate_limited_function
