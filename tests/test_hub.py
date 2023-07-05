from fastapi.testclient import TestClient
from g3py.hub import app
from g3py.metrics import MetricsModel


client = TestClient(app)


def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    d = response.json()
    assert d['status'] == 'ok'
    assert len(d['providers']) == 0
    assert len(d['subscribers']) == 0


def test_update_changed():
    mm = MetricsModel(source='test_hub', metrics=dict(speed=100, lat=0, lng=0), units=dict(speed='kph'))
    response = client.post("/update", json=mm.dict())
    assert response.status_code == 200, "expected 200-OK status from /update"

    response = client.get("/changed", params=dict(metrics="speed,lat"))
    assert response.status_code == 200, "expected 200-OK status from /changed"
    mm = MetricsModel(**response.json())
    assert mm.metrics == dict(speed=100, lat=0)
    assert mm.units == dict(speed='kph')
