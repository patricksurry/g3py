import asyncio
from uuid import uuid4
import logging
from typing import List, TypeVar, Generic, Optional


Item = TypeVar('Item')


class Subscription(Generic[Item]):
    def __init__(self, topics: List[str] = [], name: Optional[str] = None):
        self.id = str(uuid4())
        self.name = name
        self.q: asyncio.Queue[Item] = asyncio.Queue()
        self.topics = topics

    def dict(self):
        return dict(id=self.id, name=self.name, topics=self.topics)


def default_editor(item: Item, item_topic: Optional[str], client_topics: List[str]) -> Optional[Item]:
    if item_topic is None or not client_topics or item_topic in client_topics:
        return item
    else:
        return None


class Publisher(Generic[Item]):
    """Simple pub-sub mechanism so publisher can add to subscribe queues for async access"""
    def __init__(self, editor=default_editor):
        self.subs: dict[str, Subscription] = dict()
        self.editor = editor

    def subscribe(self, topics: List[str] = [], name: Optional[str] = None) -> str:
        sub = Subscription[Item](topics, name)
        self.subs[sub.id] = sub
        logging.debug(f"pub.subscribed {sub.id}")
        return sub.id

    def unsubscribe(self, id: str):
        logging.debug(f"pub.unsubscribed {id}")
        del self.subs[id]

    def publish(self, item: Item, topic: Optional[str] = None):
        for sub in self.subs.values():
            e = self.editor(item, topic, sub.topics)
            if e is not None:
                sub.q.put_nowait(e)

    async def next(self, id: str) -> Item:
        return await self.subs[id].q.get()

