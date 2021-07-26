Simple metrics server for [g3](https://github.com/patricksurry/g3).
Provides an example of fake time series to drive the G3 example gauges,
along with a stub to plug in your real simulator metrics.

Using [python3](https://www.python.org/downloads/), install required packages:

    pip install fastapi uvicorn aiofiles

Create your panel HTML file for G3 within the `panels` folder,
and specify a panel URL like `/metrics/fake.json` (or modify `metrics.py` appropriately).
For instance, a minimal panel would look like `./panels/panel.html` containing:

```html
<html>
    <body>
        <script src="https://unpkg.com/@patricksurry/g3/dist/g3-examples.min.js"></script>
        <script>
g3.panel('DHC2FlightPanel').interval(250).url('/metrics/fake.json')('body');
        </script>
    </body>
</html>
```

Start the server:

    uvicorn metrics:app --reload

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
