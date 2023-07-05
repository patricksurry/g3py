from g3py.changedict import ChangeDict
from time import sleep, time
from typing import Any


def test_update():
    d = ChangeDict[str, Any](comparators=dict(foo=lambda a, b: abs(a-b) < 8))
    t = int(time() * 1000)
    v = dict(a=1, b=2, z='zzz', foo=1024)
    d.update(**v)
    assert d.latest() >= t
    assert set(d.changed_since(0).keys()) == set(v.keys())
    sleep(1)
    c = d.update_changed(a=1, b=3, c=3, foo=1031)
    assert set(c.keys()) == {'b', 'c'}
    sleep(1)
    c = d.update_changed(a=4, foo=1033)
    assert set(c.keys()) == {'a', 'foo'}

    assert d.changed_since(t+1500) == dict(a=4, foo=1033)
