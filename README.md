Simple metrics server for [g3](https://github.com/patricksurry/g3).
Provides an example of fake time series to drive the G3 example gauges,
along with a stub to plug in your real simulator metrics.

Either use [conda](https://docs.conda.io/en/latest/miniconda.html) to create a local
python environment via:

    conda env update -f environment.yml

or manually install [python3](https://www.python.org/downloads/) and install dependencies:

    pip install fastapi uvicorn aiofiles

Create your panel HTML file for G3 within the `panels` folder,
and specify a panel URL like `/metrics/fake.json` (or modify `metricshub.py` appropriately).
For instance, a minimal panel would look like `./panels/panel.html` containing:

```html
<html>
    <body>
        <script src="https://unpkg.com/@patricksurry/g3/dist/g3-contrib.min.js"></script>
        <script>
g3.panel()
    .interval(250)
    .url('/metrics/fake.json')  // .url('/metrics/xplane.json')
    .append(
        g3.put().x(128).y(192).scale(0.9).append(g3.contrib.nav.airspeed.DHC2()),
        g3.put().x(384).y(192).scale(0.9).append(g3.contrib.nav.attitude.generic()),
        g3.put().x(640).y(192).scale(0.9).append(g3.contrib.nav.altitude.generic()),
        g3.put().x(896).y(192).scale(0.9).append(g3.contrib.radionav.VOR.generic()),

        g3.put().x(128).y(448).scale(0.9).append(g3.contrib.nav.turnCoordinator.generic()),
        g3.put().x(384).y(448).scale(0.9).append(g3.contrib.nav.heading.generic()),
        g3.put().x(640).y(448).scale(0.9).append(g3.contrib.nav.VSI.generic()),
        g3.put().x(896).y(448).scale(0.9).append(g3.contrib.radionav.ADF.generic()),
    )
    ('body');
        </script>
    </body>
</html>
```

Start the server:

    uvicorn metricshub:app --host 0.0.0.0 --reload

Point your web browser at your panel:

    http://localhost:8000/panels/panel.html

You should see a flight control panel with randomly varying metrics,
and confirm the server is serving the metrics in the log output:

```sh
INFO:     127.0.0.1:49330 - "GET /g3/index.html HTTP/1.1" 200 OK
INFO:     127.0.0.1:49330 - "GET /metrics/fake.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:49330 - "GET /metrics/fake.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:49330 - "GET /metrics/fake.json HTTP/1.1" 200 OK
```


On Windows you may need to open the port, e.g.

    netsh advfirewall firewall add rule name="TCP Port 8000" dir=in action=allow protocol=TCP localport=8000

you can remove the rule with

    netsh advfirewall firewall delete rule name="TCP Port 8000" protocol=TCP localport=8000

Notes
---

Run tests from top level as:

    python -m pytest

Clear local chromium cache headless:

    sudo rm -R /home/pi/.cache/chromium
    sudo rm -R /home/pi/.config/chromium







