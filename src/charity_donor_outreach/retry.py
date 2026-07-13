from __future__ import annotations

import random
import time
from collections.abc import Callable

from .errors import TransientProviderError


def with_retry[T](
    operation: Callable[[], T],
    *,
    max_attempts: int = 3,
    max_total_seconds: float = 30.0,
    base_delay: float = 0.25,
    sleep: Callable[[float], None] = time.sleep,
    random_value: Callable[[], float] = random.random,
) -> tuple[T, int]:
    started = time.monotonic()
    retries = 0
    for attempt in range(1, max_attempts + 1):
        try:
            return operation(), retries
        except TransientProviderError:
            if attempt == max_attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1)) * (0.5 + random_value())
            if time.monotonic() - started + delay > max_total_seconds:
                raise
            retries += 1
            sleep(delay)
    raise AssertionError("unreachable")
