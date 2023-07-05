from typing import Any, Dict
from .changedict import ChangeDict


Metric = str
MetricValue = Any
Unit = str

MetricDict = Dict[Metric, MetricValue]
MetricChangeDict = ChangeDict[Metric, MetricValue]