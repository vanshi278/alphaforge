# ML / Forecasting Module (Pillar 4 · Phase 4)

A rigorous predictive signal. The methodology matters more than the model.

**Planned components**
- Feature engineering: 15–25 features (returns over windows, RSI, volatility,
  volume ratios, momentum), aligned to forward returns with no NaN leakage.
- Target = forward-return **rank / direction**, never raw price.
- Walk-forward cross-validation (train past → test next unseen window, roll;
  never shuffle time).
- Baseline (momentum) vs model (LightGBM, optional LSTM/GRU) on identical folds.
- Evaluation by **Information Coefficient** (mean IC, IC IR).
- SHAP interpretability so the model isn't a black box.
- Wire the score into a strategy and backtest it.

**Demo target:** an honest out-of-sample IC report, e.g. "mean IC ≈ 0.04".
