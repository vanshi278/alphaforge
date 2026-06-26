from risk.kill_switch import DrawdownKillSwitch, flatten_orders


def test_triggers_on_threshold_breach():
    ks = DrawdownKillSwitch(threshold=0.20)
    for e in (100, 110, 120):                 # peak = 120
        assert ks.update(e) is False
    assert ks.update(95) is True              # 95/120 - 1 = -20.8% -> trip
    assert ks.triggered is True


def test_no_trigger_within_threshold():
    ks = DrawdownKillSwitch(threshold=0.20)
    for e in (100, 110, 120, 100):            # worst dd = -16.7%
        ks.update(e)
    assert ks.triggered is False


def test_latches_after_trigger():
    ks = DrawdownKillSwitch(threshold=0.20)
    for e in (100, 70, 200):                  # trips at 70, stays tripped even as equity recovers
        ks.update(e)
    assert ks.triggered is True


def test_flatten_orders():
    assert flatten_orders({"A": 100, "B": -50, "C": 0}) == {"A": -100, "B": 50}
