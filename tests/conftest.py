import pytest
from xprocess import ProcessStarter     # type: ignore
from os import path


HUB_PORT = 1234
APP_DIR = path.abspath(path.join(path.dirname(__file__), '..'))


# find the most logfile in ./.pytest_cache/d/.xprocess/hub_server/xprocess.log
@pytest.fixture(scope='module')
def start_hub_server(xprocess):        #  request xprocess fixture
    class HubStarter(ProcessStarter):
        # startup pattern
        pattern = "Uvicorn running on"
        timeout = 10
        terminate_on_interrupt = True

        # command to start process
        args = ['uvicorn', 'g3py.hub:app', '--app-dir', APP_DIR, '--host', '0.0.0.0', '--port', str(HUB_PORT)]

    xprocess.ensure("hub_server", HubStarter)  # returns logfile path
    yield f'http://0.0.0.0:{HUB_PORT}'

    xprocess.getinfo("hub_server").terminate()


@pytest.fixture
def start_fake_provider(xprocess):
    class FakeStarter(ProcessStarter):
        pattern = "INFO:root:fakemetrics producer started"
        timeout = 1
        terminate_on_interrupt = True

        args = ['bash', '-c', f'cd {APP_DIR} && python -m fake.fakemetrics --hub-url http://localhost:{HUB_PORT}']

    xprocess.ensure("fake_provider", FakeStarter)
    yield None
    xprocess.getinfo("fake_provider").terminate()