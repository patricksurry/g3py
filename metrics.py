from typing import Dict, Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every

#import xplane.fetch as source
import fs2020.fetch as source
#import fakemetrics as source

from changedict import ChangeDict

state = ChangeDict()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve content directly from the panels folder at /panels URL
app.mount("/panels", StaticFiles(directory="panels"), name="static")


@app.get('/')
def root_json():
    return {'status': 'ok'}


def update_with_triggers(d):
    latest = state.latest()
    state.update(d)
    out = source.triggerActions(state.changedsince(latest))
    state.update(out)


@app.get("/metrics.json")
def metrics_json(metrics: str = '', latest: int = 0, units: bool = False):
    ms = metrics.split(',') if metrics else None
    d = source.pollMetrics(ms)
    update_with_triggers(d)
    d = {
        k: v for (k, v) in state.changedsince(latest).items()
        if not ms or k in ms
    }
    result = {
        "latest": state.latest(),
        "metrics": d
    }
    if units:
        result['units'] = {
            k: v for (k, v) in source.metricUnits().items()
            if not ms or k in ms
        }
    return result


# Receive external inputs
@app.post("/inputs")
def metrics_inputs(d: Dict[str, Any]):
    update_with_triggers(d)


if hasattr(source, 'background_task'):
    freq = getattr(source, 'background_frequency_seconds', 1)

    @app.on_event("startup")
    @repeat_every(seconds=freq, raise_exceptions=True)
    def poll_events() -> None:
        source.background_task()
