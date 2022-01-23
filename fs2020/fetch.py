import json
from os import path
from ruamel.yaml import YAML
from SimConnect import *


yaml = YAML(typ='safe')

mydir = path.dirname(__file__)
with open(path.join(mydir, 'units.yml')) as f:
    units = yaml.load(f)

unitmap = {}
for std, simunits in units.keys():
    if not isinstance(simunits, list):
        simunits = [simunits]
    for u in simunits:
        unitmap[u] = std

with open(path.join(mydir, 'mapping.yml')) as f:
    mapping = yaml.load(f)['metrics']

# Create SimConnect link
sm = SimConnect()
# _time is cache length in milliseconds
aq = AircraftRequests(sm, _time=100)

for m in mapping:
    sv = aq.find(m['simvar'])
    if sv:
        unit = sv.definitions[0][1].decode('utf-8')
        m['unit'] = unitmap.get(unit, unit)
    else:
        print(f"g3py:fs2020:WARNING: No simvar for {m['simvar']}")
    m['simvar'] = sv


def pollMetrics():
    metrics = {}
    for m in mapping:
        sv = m['simvar']
        if not sv:
            continue
        v = sv.get()
        if 'fx' in m:
            v = eval(m['fx'], None, dict(x=v))
        metrics[m['metric'] + ':' + m['unit']] = v
    return metrics


if __name__ == '__main__':
    print(json.dumps(pollMetrics(), indent=4, sort_keys=True))
