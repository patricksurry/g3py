from g3py.metrics import MetricsModel
from g3py.rules import ProxyRule


def test_rules():
    mm = MetricsModel(
        source='test',
        metrics=dict(speed_kph=160),
        units=dict(speed_kph='kph')
    )
    rules = [
        ProxyRule(
            source='speed_kph',
            target='speed_mph',
            fx='x * 5/8',
            unit='mph',
        ),
        ProxyRule(
            source='speed_mph',
            target='limit_exceeded',
            fx='x > dict(mph=60, kph=100)[u]',      # test reference to source unit
        ),
    ]
    mm.apply(rules)
    assert mm.metrics['speed_mph'] == 100
    assert mm.units['speed_mph'] == 'mph'
    assert mm.metrics['limit_exceeded']
    assert 'limit_exceeded' not in mm.units, "No implied units"
