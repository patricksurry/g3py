from collections import OrderedDict
import math
from typing import Callable, Any, Dict, Generic, TypeVar
from itertools import takewhile
from time import time


def now_ms() -> int:
    return round(time() * 1000)


K = TypeVar('K')
V = TypeVar('V')

Comparator = Callable[[V, V], bool]


def equal_or_close(rel_tol=1e-6, abs_tol=1e-6) -> Comparator:
    """Return a function that decides if a ~= b"""
    def comparator(a, b) -> bool:
        try:
            v = math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
        except Exception:
            v = a == b
        return v
    return comparator


class ChangeDict(OrderedDict, Generic[K, V]):
    """An ordered dict that records timestamp of changed items"""
    def __init__(self, default_comparator: Comparator=equal_or_close(), comparators: Dict[K, Comparator]={}):
        self.__default_comparator = default_comparator
        self.__comparators = comparators
        self.__times: Dict[K, int] = {}

    def __setitem__(self, k: K, v: V) -> None:
        if k in self:
            vv = self[k]
            eq = self.__comparators.get(k, self.__default_comparator)
            if eq(v, vv):
                return
        super().__setitem__(k, v)
        self.move_to_end(k)
        self.__times[k] = now_ms()

    def __delitem__(self, k: K) -> None:
        super().__delitem__(k)
        del self.__times[k]

    def latest(self) -> int:
        if not self.__times:
            return 0
        k = next(reversed(self))
        return self.__times[k]

    def changed_since(self, ms: int) -> Dict[K, V]:
        return dict(
            takewhile(
                lambda kv: self.__times[kv[0]] > ms,
                reversed(self.items())
            )
        )

    def update_changed(self, *args, **kwargs) -> Dict[K, V]:
        """Update from d and return dict of changes"""
        latest = self.latest()
        self.update(*args, **kwargs)
        return self.changed_since(latest)


