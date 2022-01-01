from . import xpc  # Copied from https://github.com/nasa/XPlaneConnect/blob/master/Python3/src/xpc.py

from ruamel.yaml import YAML

import json
from os import path


yaml = YAML(typ='safe')
with open(path.join(path.dirname(__file__), 'mapping.yml')) as f:
    mapping = yaml.load(f)['metrics']


def pollMetrics():
    drefs = [m['dref'] for m in mapping]
    with xpc.XPlaneConnect() as client:
        vecs = client.getDREFs(drefs)
    data = dict(zip(drefs, vecs))
    metrics = {}
    for (m, vec) in zip(mapping, vecs):
        k = m['metric']
        ks = k if isinstance(k, list) else [k]
        if 'fx' in m:
            vec = [eval(m['fx'], None, dict(x=v, data=data)) for v in vec]
        unit = m.get('unit')
        unit = f':{unit}' if unit else ''
        d = {k + unit: v for (k, v) in zip(ks, vec)}
        metrics.update(d)
    return metrics


def fetchAll():
    with open(path.join(path.dirname(__file__), 'DataRefs.txt')) as f:
        drefs = [s.split()[0] for s in f.read().splitlines()[2:]]

    with xpc.XPlaneConnect() as client:
        vecs = client.getDREFs(drefs)
        data = dict(zip(drefs, vecs))

    return data


if __name__ == '__main__':
    print(json.dumps(pollMetrics(), indent=4, sort_keys=True))
    json.dump(fetchAll(), open('datarefs.json', 'w'), indent=4, sort_keys=True)
