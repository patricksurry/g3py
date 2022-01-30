from typing import Dict, List, Optional, Any

from faketimeseries import (
    timeGenerator, datetimeGenerator,
    forceSeriesGenerator, categoricalGenerator
)

# Define random metrics timeseries corresponding to the example gauges

metricGenerators = {
    'time': timeGenerator(),
    'date': datetimeGenerator(),
    'pressureSetting': forceSeriesGenerator(955, 1075),
    'altitude': forceSeriesGenerator(0, 30000, fmax=0.001),
    'pitch': forceSeriesGenerator(-25, 25),
    'roll': forceSeriesGenerator(-25, 25),
    'slip': forceSeriesGenerator(-20,20),
    'heading': forceSeriesGenerator(0, 360, wrap=True),
    'radialDeviation': forceSeriesGenerator(-10, 10),
    'radialVOR': forceSeriesGenerator(0, 360, wrap=True),
    'headingADF': forceSeriesGenerator(0, 360, wrap=True),
    'relativeADF': forceSeriesGenerator(0, 360, wrap=True),
    'verticalSpeed': forceSeriesGenerator(-1500, 1500),
    'turnrate': forceSeriesGenerator(-3, 3),
    'airspeed': forceSeriesGenerator(40, 200),
    'suctionPressure': forceSeriesGenerator(0, 10),
    'manifoldPressure': forceSeriesGenerator(10, 50),
    'fuel.front': forceSeriesGenerator(0, 26),
    'fuel.center': forceSeriesGenerator(0, 26),
    'fuel.rear': forceSeriesGenerator(0, 20),
    'fuelSelector': categoricalGenerator(['front', 'center', 'rear']),
    'engineRPM': forceSeriesGenerator(300, 3500),
    'oilPressure': forceSeriesGenerator(0, 200),
    'fuelPressure': forceSeriesGenerator(0, 10),
    'oilTemperature': forceSeriesGenerator(0, 100),
    'carbMixtureTemp': forceSeriesGenerator(-50, 50),
    'cylinderHeadTemp': forceSeriesGenerator(0, 350),
    'alternatorLoad': forceSeriesGenerator(0, 1),
    'alternatorVolts': forceSeriesGenerator(0, 30),
}

actions: List[Dict[str, Any]] = [
    dict(input='SW3-3', method='set', event='PARKING_BRAKE_SET'),
    dict(input='SW3-2', method='set', event='PITOT_HEAT_SET'),
    dict(input='ALT-ROT', method='incdec', event=['KOHLSMAN_INC', 'KOHLSMAN_DEC']),
    dict(input='ATT-BTN', event='ATTITUDE_CAGE_BUTTON'),
    dict(input='engineRPM', fx='x + 0', simvar='SomeVar'),
    dict(input='SW3-1', output='FRONT_CABIN_LIGHTS'),
    dict(input='SW3-2', output='REAR_CABIN_LIGHTS'),
    dict(input='fuelWarning', output='RED_WARNING'),
    dict(input='oilPressureWarning', output='ORANGE_WARNING'),
]


def pollMetrics(metrics: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        k: next(v)
        for (k, v) in metricGenerators.items()
        if not metrics or k in metrics
    }


def metricUnits():
    return {}


def triggerActions(inputs: Dict[str, Any]) -> Dict[str, Any]:
    outputs = dict()
    for k, v in inputs.items():
        rules = [rule for rule in actions if rule.get('input') == k]
        if not rules:
            continue
        for rule in rules:
            if 'fx' in rule:
                v = eval(rule['fx'], None, dict(x=v))
            print(f"action {rule['input']}({v})")
            # simple copy from input to output
            if 'output' in rule:
                print(f"set output {rule['output']} = {v}")
                outputs[rule['output']] = v
            elif 'simvar' in rule:
                print(f"set simvar {rule['simvar']} = {v}")
            elif 'event' in rule:
                name = rule['event']
                method = rule.get('method')
                if method == 'incdec':
                    name = name[0 if v > 0 else 1]
                if method == 'incdec':
                    v = abs(v)
                    print(f"trigger {name}() * {v}")
                elif method == 'set':
                    print(f"trigger {name}({v})")
                else:
                    print(f"trigger {name}()")
            else:
                print(f"Warning: malformed rule {rule}")
    return outputs
