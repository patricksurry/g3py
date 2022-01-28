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


def pollMetrics(metrics):
    return {
        k: next(v)
        for (k, v) in metricGenerators.items()
        if not metrics or k in metrics
    }


def metricUnits():
    return {}
