from pydantic import BaseModel, Field
import logging
import json
from typing import Optional, List, Dict, Callable
import aiohttp
from aiohttp.client_exceptions import ClientPayloadError, ClientConnectionError
from aiohttp_sse_client import client as sse_client         # type: ignore

from .decl import Metric, MetricValue, Unit
from .changedict import ChangeDict, now_ms
from .rules import ProxyRule


class MetricsModel(BaseModel):
    source: str = 'anonymous'
    latest: int = Field(default_factory=now_ms)
    metrics: Dict[Metric, MetricValue] = {}
    units: Dict[Metric, Optional[Unit]] = {}

    def apply(self, rules: List[ProxyRule]):
        for r in rules: r.apply(self.metrics, self.units)

    def filter(self, ms: List[Metric]) -> 'MetricsModel':
        return MetricsModel(
            source=self.source,
            latest=self.latest,
            metrics={m: v for m, v in self.metrics.items() if m in ms},
            units={m: v for m, v in self.units.items() if m in ms},
        )


class MetricsTracker:
    def __init__(self, source: str):
        self.source = source
        self.metrics = ChangeDict[Metric, MetricValue]()
        self.units: Dict[Metric, Optional[Unit]] = {}

    def _mm(self, ms: List[Metric]):
        return MetricsModel(
            source=self.source,
            latest=self.metrics.latest(),
            metrics={m: v for m, v in self.metrics.items() if m in ms},
            units={m: v for m, v in self.units.items() if m in ms},
        )

    def update_changed(self, mm: MetricsModel) -> Optional[MetricsModel]:
        self.units.update(mm.units)
        ms = list(self.metrics.update_changed(mm.metrics).keys())
        return self._mm(ms) if ms else None

    def snapshot(self, since: int = 0) -> MetricsModel:
        ms = list(self.metrics.changed_since(since).keys())
        return self._mm(ms)


class MetricsProducer:
    endpoint = '/update'

    """Publish metric updates and actions to hub as MetricsModel"""
    def __init__(self, name: str, hub_url: str):
        self.hub = hub_url + self.endpoint
        self.state = MetricsTracker(name)

    async def update_async(self, mm: MetricsModel) -> Optional[bool]:
        changes = self.state.update_changed(mm)
        if not changes:
            return None

        s = f"MetricsProducer[{self.state.source}].update_async"
        status = False
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.hub, json=changes.dict()) as response:
                    status = response.status == 200
                    if not status:
                        logging.warning(f"{s}: POST {self.hub} status {response}")
            except (ClientConnectionError) as exc:
                logging.warning(f"{s}: ignoring exception {exc}")
        return status


class MetricsConsumer:
    endpoint = '/subscribe'

    """Watch for changes in a list of metrics from hub using a handler"""
    def __init__(self, name: str, hub_url: str):
        self.name = name
        self.hub = hub_url + self.endpoint

    async def watch(self, metrics: List[Metric], handler: Callable[[MetricsModel], None]):
        params = dict(name=self.name, metrics=','.join(metrics), since=0)
        logging.debug(f"MetricConsumer[{self.name}]: consuming {metrics} via {params}")
        while True:
            async with sse_client.EventSource(self.hub, params=params) as events:
                try:
                    async for event in events:
                        if event.type == 'ping':
                            logging.debug(f"Ignoring ping {event}")
                            continue
                        mm = MetricsModel(**json.loads(event.data))
                        params['since'] = mm.latest
                        logging.debug(f"MetricsConsumer[{self.name}].watch: got SSE event data {event.data}")
                        handler(mm)
                except (ConnectionError, ClientPayloadError) as exc:
                    logging.warning(f"MetricsConsumer[{self.name}].watch: ignoring exception {exc}")
            logging.debug(f"MetricConsumer[{self.name}]: restarting")
