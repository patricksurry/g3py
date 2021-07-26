from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from faketimeseries import (
    timeGenerator, datetimeGenerator,
    forceSeriesGenerator, categoricalGenerator
)

# Define random metrics timeseries corresponding to the example gauges

metricGenerators = dict(
    time=timeGenerator(),
    date=datetimeGenerator(),
    atmosphericPressure=forceSeriesGenerator(955, 1075),
    altitude=forceSeriesGenerator(0, 30000, fmax=0.001),
    pitch=forceSeriesGenerator(-25, 25),
    roll=forceSeriesGenerator(-25, 25),
    heading=forceSeriesGenerator(0, 360, wrap=True),
    radialDeviation=forceSeriesGenerator(-10, 10),
    radialVOR=forceSeriesGenerator(0, 360, wrap=True),
    headingADF=forceSeriesGenerator(0, 360, wrap=True),
    relativeADF=forceSeriesGenerator(0, 360, wrap=True),
    verticalSpeed=forceSeriesGenerator(-1500, 1500),
    turnrate=forceSeriesGenerator(-3, 3),
    airspeed=forceSeriesGenerator(40, 200),
    suctionPressure=forceSeriesGenerator(0, 10),
    manifoldPressure=forceSeriesGenerator(10, 50),
    fuelFront=forceSeriesGenerator(0, 26),
    fuelCenter=forceSeriesGenerator(0, 26),
    fuelRear=forceSeriesGenerator(0, 20),
    fuelSelector=categoricalGenerator(['front', 'center', 'rear']),
    engineTachometer=forceSeriesGenerator(300, 3500),
    oilPressure=forceSeriesGenerator(0, 200),
    fuelPressure=forceSeriesGenerator(0, 10),
    oilTemperature=forceSeriesGenerator(0, 100),
    cylinderHeadTemp=forceSeriesGenerator(-50, 50),
)


app = FastAPI()

# Serve content directly from the panels folder at /panels URL
app.mount("/panels", StaticFiles(directory="panels"), name="static")


# Serve random metrics
@app.get("/metrics/fake.json")
def metrics_fake():
    return {k: next(v) for (k, v) in metricGenerators.items()}


# Serve live metrics from your actual source
@app.get("/metrics/live.json")
def metrics_live():
    return {}       #TODO: fill this in
