from random import random
from datetime import datetime


def datetimeGenerator():
    while True:
        yield datetime.now().isoformat()


def timeGenerator():
    while True:
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yield (now - midnight).total_seconds()


def forceSeriesGenerator(min=0, max=1, fmax=0.01, damping=0.9, wrap=False):
    x = random()
    v = 0
    while True:
        yield x * (max - min) + min
        x += v
        v += (2*random()-1)*fmax
        v *= damping
        if x < 0 or x > 1:
            if not wrap:
                v = -v
                x = -x if x < 0 else 2-x
            else:
                x = x - 1 if x > 1 else x + 1


def categoricalGenerator(values):
    n = len(values)
    vs = forceSeriesGenerator(min=0, max=n, wrap=True)
    while True:
        yield values[min(int(next(vs)), n-1)]
