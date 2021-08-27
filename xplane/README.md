Illustrates an [X-Plane](https://www.x-plane.com/) adapter for
[G3](https://github.com/patricksurry/g3),
fetching metrics from XPlane via NASA's
[XPlaneConnect](https://github.com/nasa/XPlaneConnect/) plugin.

This repo includes a copy of
[xpc.py](https://github.com/nasa/XPlaneConnect/blob/master/Python3/src/xpc.py)
which is XPlaneConnect's Python client.

Individual metrics from XPlane,
called [datarefs](https://developer.x-plane.com/datarefs/),
are mapped to G3 gauge metrics as described in mapping.yml,
and supports both simple transformation and automated unit conversion.

You can test your mapping by starting up XPlane
and running this command from the parent folder.

```sh
python -m xplane.fetch
```

You should see a dump of the currently mapped metrics:

```json
{
    "airspeed": {
        "unit": "knot",
        "value": 66.05368041992188
    },
    "altitude": {
        "unit": "ft",
        "value": 7488.25341796875
    },
    "compass": {
        "unit": "deg",
        "value": 10.877249717712402
    },
    ...
```
