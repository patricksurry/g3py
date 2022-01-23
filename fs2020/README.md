Collect metrics from MS Flight Simulator 2020, using the
[Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)
interface.

MSFS provides many [SimVars](https://docs.flightsimulator.com/html/index.htm?#t=Programming_Tools%2FSimVars%2FSimulation_Variables.htm)
which are mapped to G3 gauges via the mapping defined in `mapping.yml`.
SimVars units should be discovered automatically and tranformed to
match your specified gauge units.


You can test your mapping by starting up MSFS
and running this command from the parent folder.

```sh
python -m fs2020.fetch
```

You should see a dump of the currently mapped metrics:

SIMCONNECT_EXCEPTION_UNRECOGNIZED_ID: in (b'ENG N1 RPM:1', b'Rpm (0 to 16384 = 0 to 100%)')
SIMCONNECT_EXCEPTION_UNRECOGNIZED_ID: in (b'ENG MANIFOLD PRESSURE:1', b'inHG.')

```json
{
    "airspeed:Knots": 0.0,
    "altitude:Feet": 108.50824737548828,
    "compass:Degrees": 229.14576721191406,
    "cylinderHeadTemp:Rankine": 781.202915998182,
    "engineRPM:Rpm (0 to 16384 = 0 to 100%)": null,
    "heading:Radians": 3.998244922257538,
    "manifoldPressure:inHG.": null,
    "oilPressure:foot pounds": 270863.0178080027,
    "oilTemperature:Rankine": 628.7004895557371,
    "pitch:Radians": -0.011671489104628563,
    "pressureSetting:Millibars": 1009.2831420898438,
    "roll:Radians": 0.000904008926145336,
    "slip:Position": -0.0078125,
    "turnrate:Radians per second": 7.495487400080828e-07,
    "verticalSpeed:feet/minute": -0.03363388823345297
}
```
