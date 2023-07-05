import pytest
from asyncio import wait_for
from typing import Optional, List

from g3py.apub import Publisher


def test_publish():
    pub = Publisher[str]()
    pub.publish('apple')
    pub.publish('banana', topic='fruit')
    pub.publish('cherry', 'fruit')


@pytest.mark.asyncio()
async def test_simple():
    pub = Publisher[str]()
    sid = pub.subscribe(['fruit'])
    pub.publish('apple')
    pub.publish('banana', topic='yellow')
    pub.publish('cherry', 'fruit')

    assert await wait_for(pub.next(sid), 1) == 'apple'
    assert await wait_for(pub.next(sid), 1) == 'cherry'
    pub.unsubscribe(sid)


def mask_editor(item: str, _: Optional[str], client_topics: List[str]) -> Optional[str]:
    """Simple editor that uses client topic strings to mask characters from the source item"""
    mask = set(''.join(client_topics))
    v = [c for c in item if c in mask]
    return ''.join(v) if v else None


@pytest.mark.asyncio
async def test_editor():
    pub = Publisher[str](mask_editor)
    sid = pub.subscribe('abcde'.split())
    pub.publish('apple')
    pub.publish('banana')
    pub.publish('cherry', 'ignored')
    assert await wait_for(pub.next(sid), 1) == 'ae'
    assert await wait_for(pub.next(sid), 1) == 'baaa'
    assert await wait_for(pub.next(sid), 1) == 'ce'
    pub.unsubscribe(sid)