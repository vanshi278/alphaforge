import numpy as np

from risk.var import (historical_cvar, historical_var, monte_carlo_var,
                      parametric_cvar, parametric_var)


def test_three_methods_agree_on_normal_data():
    r = np.random.default_rng(0).normal(0, 0.01, 20_000)
    hv = historical_var(r, 0.99)
    pv = parametric_var(r, 0.99)
    mv, _ = monte_carlo_var(r, 0.99, seed=1)
    assert abs(hv - pv) < 0.002
    assert abs(mv - pv) < 0.002
    assert 0.020 < pv < 0.027        # ~ 2.326 * 0.01


def test_cvar_at_least_var():
    r = np.random.default_rng(1).normal(0, 0.01, 20_000)
    assert historical_cvar(r, 0.99) >= historical_var(r, 0.99)
    assert parametric_cvar(r, 0.99) >= parametric_var(r, 0.99)


def test_var_is_positive_loss():
    r = np.random.default_rng(2).normal(0.0005, 0.02, 5_000)
    assert historical_var(r, 0.99) > 0
