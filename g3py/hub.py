"""
The metrics hub maintains a central shared state where publishers
can write persistent updates and share ephemeral actions.

Clients can query the current state, or subscribe for ongoing SSE updates.
Metrics prefixed by the 'at' sign are not persisted as "current state"
but are included in change events.
They can be used as actions, for example ALTITUDE=100 sets the
current state of the ALTITUDE metric to 100, whereas @ALTITUDE=3
might indicate an increment of 3 to be applied,
or some explicit event object like @ALTITUDE={inc: 3}.

The following endpoints are provided:

    GET /status

    GET /changed ? metrics:str[,] & since:int? & units:bool -> MetricsModel

    GET /subscribe ? metrics:str[,] & since:int? -> MetricsModel

    POST /update MetricsModel
"""

from typing import Dict, List, Optional
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sse_starlette.sse import EventSourceResponse
import logging
import json
from os import path

from .apub import Publisher

from .metrics import MetricsProducer, MetricsConsumer, MetricsModel, MetricsTracker
from .rules import read_proxy_rules


# logging.basicConfig(level=logging.DEBUG)   # NB. separate from uvicorn --log-level argument

THIS_DIR = path.dirname(__file__)
PANELS_PATH = path.abspath(path.join(THIS_DIR, '../panels'))
CONFIG_PATH = path.abspath(path.join(THIS_DIR, 'config.yml'))


config = read_proxy_rules(CONFIG_PATH)
tracker = MetricsTracker('hub')
providers: Dict[str, MetricsTracker] = {}


def mm_editor(mm: MetricsModel, _, client_metrics: List[str]) -> Optional[MetricsModel]:
    changes = mm.filter(client_metrics)
    return changes if changes.metrics else None


pub = Publisher[MetricsModel](mm_editor)


def _split_metrics(metrics_csv: Optional[str]=None) -> List[str]:
    """splits a comma-separated string of values to list, with empty string => []"""
    return [s.strip() for s in metrics_csv.split(',')] if metrics_csv else []


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static content directly from the panels folder at /panels URL
app.mount("/panels", StaticFiles(directory=PANELS_PATH), name="static")


@app.get('/status')
def api_status():
    return dict(
        status='ok',
        providers=[p.snapshot().dict() for p in providers.values()],
        subscribers=[s.dict() for s in pub.subs.values()]
    )


# Receive external inputs
@app.post(MetricsProducer.endpoint)
def api_update(mm: MetricsModel):
    logging.debug(f'/update with {mm.dict()}')
    # track who's supplying which metrics
    if mm.source not in providers:
        providers[mm.source] = MetricsTracker(mm.source)
    providers[mm.source].update_changed(mm)

    # apply proxy rules
    mm.apply(config)

    # check for changes
    changes = tracker.update_changed(mm)

    # publish any changes
    if changes:
        logging.debug(f'hub:update publishing {changes}')
        pub.publish(changes)


@app.get(MetricsConsumer.endpoint)
async def api_subscribe(request: Request, bg: BackgroundTasks, name: Optional[str]=None, metrics: Optional[str]=None, since: int=0):
    logging.debug(f"subscription request name={name}, metrics={metrics}, since={since}")
    ms = _split_metrics(metrics)
    # produce a stream of MetricsModel events by subscribing to the hub ...
    sid = pub.subscribe(ms, name=name)
    # ... and dropping the subscription when the client quits
    bg.add_task(pub.unsubscribe, sid)

    async def subscriber():
        logging.debug(f"subscriber[{sid}] subscribed for {ms}")
        # first send current state
        mm = tracker.snapshot(since).filter(ms)
        yield dict(data=json.dumps(mm.dict()))
        # ... then send ongoing subscription results
        while not await request.is_disconnected():
            logging.debug(f"subscriber[{sid}] yield")
            mm = await pub.next(sid)
            yield dict(data=json.dumps(mm.dict()))
        logging.debug(f"subscriber[{sid}] disconnected")

    return EventSourceResponse(subscriber())


@app.get("/changed")
def api_changed(metrics: str = '', since: int = 0) -> MetricsModel:
    """Get a one-off update"""
    changes = tracker.snapshot(since)
    if metrics:
        changes = changes.filter(_split_metrics(metrics))
    return changes

