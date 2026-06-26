from risk.limits import RiskLimits, RiskManager


def test_resize_to_per_position_cap():
    rm = RiskManager(RiskLimits(max_position_pct=0.2, max_gross_pct=5.0))
    appr, reason = rm.check_order("X", 1000, 100.0, {"X": 0}, {"X": 100.0}, equity=100_000.0)
    assert appr == 200 and reason == "resized"      # 20% of 100k / 100 = 200 shares


def test_block_when_already_at_cap():
    rm = RiskManager(RiskLimits(max_position_pct=0.2, max_gross_pct=5.0))
    appr, reason = rm.check_order("X", 50, 100.0, {"X": 200}, {"X": 100.0}, equity=100_000.0)
    assert appr == 0 and reason == "blocked"


def test_risk_reducing_order_always_ok():
    rm = RiskManager(RiskLimits())
    appr, reason = rm.check_order("X", -100, 100.0, {"X": 200}, {"X": 100.0}, equity=100_000.0)
    assert appr == -100 and reason == "ok"


def test_gross_cap_binds_across_names():
    rm = RiskManager(RiskLimits(max_position_pct=1.0, max_gross_pct=1.0))
    positions = {"X": 0, "Y": 800}                  # Y uses 80% of the 100% gross budget
    prices = {"X": 100.0, "Y": 100.0}
    appr, reason = rm.check_order("X", 1000, 100.0, positions, prices, equity=100_000.0)
    assert appr == 200 and reason == "resized"      # only 20% gross headroom left
