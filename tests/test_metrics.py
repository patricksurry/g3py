from g3py.metrics import MetricsModel


def test_filter():
    mm = MetricsModel(
        latest=1234,
        source='test',
        metrics=dict(x=1, y=2, z=3),
        units=dict(x='m')
    )
    assert not mm.filter(['a']).metrics
    f = mm.filter(['x', 'y'])
    assert f is not None
    assert list(f.metrics.keys()) == ['x', 'y']
    assert f.latest == 1234
