# https://developer.x-plane.com/datarefs/

from . import xpc

import json
from os import path

drefs = json.load(open(path.join(path.dirname(__file__), 'mapping.json')))


def pollMetrics():
    with xpc.XPlaneConnect() as client:
        vecs = client.getDREFs(drefs.keys())
    metrics = {}
    for (vec, ms) in zip(vecs, drefs.values()):
        metrics.update(zip(ms if isinstance(ms, list) else [ms], vec))

    #TODO these conversions should be somewhere else
    if 'pressureSetting' in metrics:
        metrics['pressureSetting'] *= 33.8639  # inches of mercury => hectopascals
    if 'toFrVOR' in metrics:
        # 0 is flag, 1 is to, 2 is from.
        metrics['reliabilityVOR'] = metrics['toFrVOR'] == 0
        metrics['toFrVOR'] -= 1  # to=0, from=1
    return metrics


if __name__ == '__main__':
    print(json.dumps(pollMetrics(), indent=4, sort_keys=True))
