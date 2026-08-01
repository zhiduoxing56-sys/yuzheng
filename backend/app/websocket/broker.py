from __future__ import annotations

import asyncio
from collections import defaultdict
from threading import RLock

from app.models.schemas import PipelineEvent
from app.core.redaction import SensitiveDataRedactor


class PipelineEventBroker:
    """Non-blocking, session-isolated bridge from sync pipeline threads to WebSockets."""

    def __init__(self, queue_size: int = 256) -> None:
        self._lock = RLock()
        self._queue_size = queue_size
        self._subscribers: dict[
            str, list[tuple[asyncio.AbstractEventLoop, asyncio.Queue[PipelineEvent]]]
        ] = defaultdict(list)
        self._session_sequences: dict[str, int] = {}

    def subscribe(
        self, session_id: str
    ) -> tuple[asyncio.AbstractEventLoop, asyncio.Queue[PipelineEvent]]:
        subscription = (asyncio.get_running_loop(), asyncio.Queue(self._queue_size))
        with self._lock:
            self._subscribers[session_id].append(subscription)
        return subscription

    def unsubscribe(
        self,
        session_id: str,
        subscription: tuple[asyncio.AbstractEventLoop, asyncio.Queue[PipelineEvent]],
    ) -> None:
        with self._lock:
            subscribers = self._subscribers.get(session_id, [])
            if subscription in subscribers:
                subscribers.remove(subscription)
            if not subscribers:
                self._subscribers.pop(session_id, None)
                self._session_sequences.pop(session_id, None)

    @staticmethod
    def _put_nowait(queue: asyncio.Queue[PipelineEvent], event: PipelineEvent) -> None:
        if queue.full():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
        queue.put_nowait(event)

    def publish(self, event: PipelineEvent) -> None:
        with self._lock:
            subscribers = list(self._subscribers.get(event.session_id, []))
            if subscribers:
                sequence = self._session_sequences.get(event.session_id, 0) + 1
                self._session_sequences[event.session_id] = sequence
            else:
                sequence = event.sequence
        event = PipelineEvent.model_validate(
            SensitiveDataRedactor.redact(
                event.model_copy(update={"sequence": sequence}).model_dump(mode="json")
            )
        )
        for loop, queue in subscribers:
            if loop.is_closed():
                continue
            loop.call_soon_threadsafe(self._put_nowait, queue, event)

    def subscriber_count(self, session_id: str | None = None) -> int:
        with self._lock:
            if session_id is not None:
                return len(self._subscribers.get(session_id, []))
            return sum(len(items) for items in self._subscribers.values())
