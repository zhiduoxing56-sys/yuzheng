from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import Condition, RLock
from typing import Callable, Generic, TypeVar, cast


T = TypeVar("T")


@dataclass(frozen=True)
class ReadCacheStats:
    hits: int
    misses: int
    waits: int
    computations: int
    invalidations: int
    evictions: int
    entries: int
    running: int


class BoundedSingleFlightCache(Generic[T]):
    """Small process-local LRU cache with one computation per key.

    Cached values must be read-only response objects. Authorization material and raw
    request bodies must never be passed to this cache.
    """

    def __init__(self, max_entries: int = 128) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._max_entries = max_entries
        self._values: OrderedDict[str, T] = OrderedDict()
        self._running: set[str] = set()
        self._lock = RLock()
        self._condition = Condition(self._lock)
        self._hits = 0
        self._misses = 0
        self._waits = 0
        self._computations = 0
        self._invalidations = 0
        self._evictions = 0

    def get_or_compute(self, key: str, compute: Callable[[], T]) -> T:
        with self._condition:
            while True:
                if key in self._values:
                    value = self._values.pop(key)
                    self._values[key] = value
                    self._hits += 1
                    return value
                if key not in self._running:
                    self._running.add(key)
                    self._misses += 1
                    self._computations += 1
                    break
                self._waits += 1
                self._condition.wait()

        try:
            value = compute()
        except BaseException:
            with self._condition:
                self._running.discard(key)
                self._condition.notify_all()
            raise

        with self._condition:
            self._running.discard(key)
            self._values[key] = value
            self._values.move_to_end(key)
            while len(self._values) > self._max_entries:
                self._values.popitem(last=False)
                self._evictions += 1
            self._condition.notify_all()
        return value

    def get(self, key: str) -> T | None:
        with self._condition:
            if key not in self._values:
                return None
            value = self._values.pop(key)
            self._values[key] = value
            self._hits += 1
            return cast(T, value)

    def invalidate(self, key: str) -> None:
        with self._condition:
            if self._values.pop(key, None) is not None:
                self._invalidations += 1

    def invalidate_prefix(self, prefix: str) -> None:
        with self._condition:
            keys = [key for key in self._values if key.startswith(prefix)]
            for key in keys:
                del self._values[key]
            self._invalidations += len(keys)

    def stats(self) -> ReadCacheStats:
        with self._condition:
            return ReadCacheStats(
                hits=self._hits,
                misses=self._misses,
                waits=self._waits,
                computations=self._computations,
                invalidations=self._invalidations,
                evictions=self._evictions,
                entries=len(self._values),
                running=len(self._running),
            )
