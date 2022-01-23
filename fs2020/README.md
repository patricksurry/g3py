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

```json
{
    ...
}
```
