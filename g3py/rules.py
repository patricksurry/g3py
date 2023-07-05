from pydantic import BaseModel, PrivateAttr
from typing import Optional, Dict
from types import CodeType
from ruamel.yaml import YAML

from .decl import  Metric, MetricValue, Unit

yaml = YAML(typ='safe')


class ProxyRule(BaseModel):
    source: Metric
    target: Metric
    unit: Optional[Metric]
    fx: str = 'x'
    _fx: CodeType = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._fx = compile(self.fx, '<string>', 'eval')

    def apply(self, metrics: Dict[Metric, MetricValue], units: Dict[Metric, Optional[Unit]]) -> None:
        if self.source not in metrics:
            return
        u = units.get(self.source)
        metrics[self.target] = eval(self._fx, None, dict(x=metrics[self.source], u=u))
        if self.unit:
            units[self.target] = self.unit


def read_proxy_rules(filename: str):
    with open(filename) as f:
        rules = [ProxyRule(**r) for r in yaml.load(f)]
    return rules
