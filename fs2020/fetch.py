from typing import Dict, List, Optional, Any
import json
from os import path
from ruamel.yaml import YAML
from simconnect import SimConnect, PERIOD_VISUAL_FRAME
import logging


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
sc = SimConnect()
dd = sc.subscribe_simdata(
    [m['simvar'] for m in mapping],
    period=PERIOD_VISUAL_FRAME,
    interval=10,
)
simvars = dd.get_units()
latest = 0

for m in mapping:
    unit = simvars.get(m['simvar'])
    if m['simvar'] in simvars:
        unit = simvars[m['simvar']]
        m['unit'] = unitmap.get(unit, unit)
    else:
        print(f"g3py:fs2020:WARNING: No simvar for {m['simvar']}")


def process_simconnect_events():
#    logging.debug("exhausting simconnect queue")
    while sc.receive():
        pass


def pollMetrics(metrics: Optional[List[str]] = None) -> Dict[str, Any]:
    global latest
    process_simconnect_events()
    recent = dd.simdata.changedsince(latest)
    latest = dd.simdata.latest()
    data = {}
    for m in mapping:
        name = m['metric']
        sv = m['simvar']
        if metrics and name not in metrics or sv not in recent:
            continue
        v = recent[sv]
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
            # set a simulation variable
            elif 'simvar' in rule:
                sc.set_simdatum(rule['simvar'], v)
            # generate an event
            elif 'event' in rule:
                name = rule['event']
                method = rule.get('method')
                if method == 'incdec':
                    name = name[0 if v > 0 else 1]
                # trigger an inc / dec event a number of times
                if method == 'incdec':
                    v = abs(v)
                    while v > 0:
                        sc.send_event(name)
                        v -= 1
                # trigger an event with a data value
                elif method == 'set':
                    sc.send_event(name, v)
                # just trigger an event
                else:
                    sc.send_event(name)
            else:
                print(f"Warning: malformed rule {rule}")
    return outputs


if __name__ == '__main__':
    print(json.dumps(metricUnits(), indent=4, sort_keys=True))
    print(json.dumps(pollMetrics(), indent=4, sort_keys=True))
