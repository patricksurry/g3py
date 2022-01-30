from typing import Dict, List, Optional, Any
import json
from os import path
from ruamel.yaml import YAML
from SimConnect import SimConnect, AircraftEvents, AircraftRequests


yaml = YAML(typ='safe')

mydir = path.dirname(__file__)
with open(path.join(mydir, 'units.yml')) as f:
    units = yaml.load(f)

unitmap = {}
for std, simunits in units.items():
    if not isinstance(simunits, list):
        simunits = [simunits]
    for u in simunits:
        unitmap[u] = std

with open(path.join(mydir, 'mapping.yml')) as f:
    cfg = yaml.load(f)
    mapping = cfg['metrics']
    actions = cfg['actions']


# Create SimConnect link
sm = SimConnect()
# _time is cache length in milliseconds
aq = AircraftRequests(sm, _time=100)
ae = AircraftEvents(sm)

for m in mapping:
    sv = aq.find(m['simvar'])
    if sv:
        unit = sv.definitions[0][1].decode('utf-8')
        m['unit'] = unitmap.get(unit, unit)
    else:
        print(f"g3py:fs2020:WARNING: No simvar for {m['simvar']}")
    m['simvar'] = sv


def pollMetrics(metrics: Optional[List[str]] = None) -> Dict[str, Any]:
    data = {}
    for m in mapping:
        name = m['metric']
        if metrics and name not in metrics:
            continue
        sv = m['simvar']
        if not sv:
            continue
        v = sv.get()
        if 'fx' in m:
            v = eval(m['fx'], None, dict(x=v))
        data[name] = v
    return data


def metricUnits():
    return {m['metric']: m['unit'] for m in mapping}


def triggerActions(inputs: Dict[str, Any]) -> Dict[str, Any]:
    outputs = dict()
    for k, v in inputs.items():
        rules = [rule for rule in actions if rule.get('input') == k]
        if not rules:
            continue
        for rule in rules:
            if 'fx' in rule:
                v = eval(rule['fx'], None, dict(x=v))
            # simple copy from input to output
            if 'output' in rule:
                outputs[rule['output']] = v
            elif 'simvar' in rule:
                sv = mapping.get(rule['simvar'])
                if not sv:
                    print(f"Warning: {rule['simvar']} not found for input {k}")
                else:
                    sv.set(v)
            elif 'event' in rule:
                name = rule['event']
                method = rule.get('method')
                if method == 'incdec':
                    name = name[0 if v > 0 else 1]
                ev = ae.find(name)
                if not ev:
                    continue
                if method == 'incdec':
                    v = abs(v)
                    while v > 0:
                        ev()
                        v -= 1
                elif method == 'set':
                    ev(v)
                else:
                    ev()
            else:
                print(f"Warning: malformed rule {rule}")
    return outputs


if __name__ == '__main__':
    print(json.dumps(metricUnits(), indent=4, sort_keys=True))
    print(json.dumps(pollMetrics(), indent=4, sort_keys=True))
