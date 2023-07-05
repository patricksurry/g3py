import pytest
import httpx
import asyncio
from asyncio import wait_for, gather

from g3py.metrics import MetricsModel, MetricsProducer, MetricsConsumer



def test_status(start_hub_server):
    response = httpx.get(start_hub_server + '/status').json()
    assert response['status'] == 'ok'


@pytest.mark.asyncio
async def test_update(start_hub_server):
    provider = MetricsProducer('test', start_hub_server)
    assert await provider.update_async(MetricsModel(metrics={'speed': 100})) == True


@pytest.mark.asyncio
async def test_subscribe(start_hub_server):
    def update(fuel: float, oil: float):
        print('sending update', fuel, oil)
        httpx.post(
            start_hub_server + '/update',
            json=MetricsModel(metrics=dict(fuelPressure=fuel, oilPressure=oil)).dict()
        )

    async def sleep_then_update(fuel, oil):
        await asyncio.sleep(0.5)
        update(fuel, oil)

    consumer = MetricsConsumer('test_consumer', start_hub_server)
    lights = dict()

    def handler(mm: MetricsModel):
        print('handler got update', mm)
        lights.update(mm.metrics)

    update(0, 0)

    try:
        await wait_for(gather(
            consumer.watch(['ORANGE_WARNING', 'RED_WARNING'], handler),
            sleep_then_update(10, 200)
        ), 1)
    except asyncio.TimeoutError:
        # expected to kill the subscription
        pass

    assert lights == dict(ORANGE_WARNING=True, RED_WARNING=True)
