from time import sleep
import httpx

from g3py.metrics import MetricsModel


def test_fake(start_hub_server, start_fake_provider):
    sleep(3)
    response = httpx.get(start_hub_server + '/status').json()
    assert response['status'] == 'ok'
    mms = [MetricsModel(**d) for d in response['providers']]
    mm = next((mm for mm in mms if mm.source == 'fakemetrics'), None)
    assert mm
    assert 'oilPressure' in mm.metrics

    response = httpx.get(start_hub_server + '/changed').json()
    mm = MetricsModel(**response)
    assert mm.metrics
