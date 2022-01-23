import json
from os import path
from ruamel.yaml import YAML
from SimConnect import *


# Create SimConnect link
sm = SimConnect()
# _time is cache length in milliseconds
aq = AircraftRequests(sm, _time=100)

yaml = YAML(typ='safe')
with open(path.join(path.dirname(__file__), 'mapping.yml')) as f:
    mapping = yaml.load(f)['metrics']

for m in mapping:
    m['simvar'] = aq.find(m['simvar'])


def pollMetrics():
    metrics = {}
    for m in mapping:
        if not m['simvar']:
            continue
        v = m['simvar'].get()
        unit = m['simvar'].definitions[0][1]
        if 'fx' in m:
            v = eval(m['fx'], None, dict(x=v))
        metrics[m['metric'] + ':' + unit] = v
    return metrics


if __name__ == '__main__':
    print(json.dumps(pollMetrics(), indent=4, sort_keys=True))
