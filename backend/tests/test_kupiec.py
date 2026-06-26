import numpy as np
import pytest

from risk.kupiec import kupiec_pof, var_exceptions


def test_well_calibrated_model_not_rejected():
    kp = kupiec_pof(n_obs=1000, n_exceptions=10, confidence=0.99)   # exactly expected
    assert kp["reject_model"] is False
    assert kp["expected"] == pytest.approx(10.0)


def test_too_many_exceptions_rejected():
    kp = kupiec_pof(n_obs=1000, n_exceptions=50, confidence=0.99)   # 5x too many
    assert kp["reject_model"] is True


def test_var_exceptions_on_normal_is_reasonable():
    r = np.random.default_rng(0).normal(0, 0.01, 2000)
    n, exc = var_exceptions(r, window=250, confidence=0.99)
    assert n == 1750
    assert 0 < exc < 0.05 * n          # roughly the 1% rate, with slack
