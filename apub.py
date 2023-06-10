import asyncio
from uuid import uuid4
import logging
from typing import Any, List


class Subscription:
    def __init__(self, topics: List[str] = []):
        self.id = str(uuid4())
        self.q: asyncio.Queue = asyncio.Queue()
        self.topics = topics


class Publisher:
    """Simple pub-sub mechanism so publisher can add to subscribe queues for async access"""
    def __init__(self):
        self.subs: dict[str, Subscription] = dict()

    def subscribe(self, topics: List[str] = []) -> str:
        sub = Subscription(topics)
        self.subs[sub.id] = sub
        logging.debug(f"pub.subscribed {sub.id}")
        return sub.id

    def unsubscribe(self, id):
        logging.debug(f"pub.unsubscribed {id}")
        del self.subs[id]

    def publish(self, item: Any, topic: str = None):
        for sub in self.subs.values():
            if topic in sub.topics or ...
                sub.q.put_nowait(item)

    async def next(self, id) -> Any:
        return await self.subs[id].q.get()

