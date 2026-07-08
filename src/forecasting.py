"""Forecasting utilities using statsmodels ARIMA/SARIMAX."""

from __future__ import annotations

import warnings

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def build_timeseries(
    df: pd.DataFrame,
    value_col: str = "credit_crore",
    sector: str | None = None,
    state: str | None = None,
) -> pd.DataFrame:
    """Create an annual time series filtered by optional sector and state."""
    data = df.copy()
    if sector and "sector" in data:
        data = data[data["sector"] == sector]
    if state:
        data = data[data["state"] == state]
    ts = data.groupby("year", as_index=False)[value_col].sum().sort_values("year")
    ts["date"] = pd.to_datetime(ts["year"].astype(str) + "-03-31")
    return ts[["date", "year", value_col]]


def forecast_credit(ts: pd.DataFrame, horizon: int, value_col: str = "credit_crore") -> pd.DataFrame:
    """Forecast future values with a compact ARIMA model and confidence intervals."""
    if len(ts) < 4:
        raise ValueError("At least four annual observations are required for forecasting.")
    series = ts.set_index("date")[value_col].asfreq("YE-MAR")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            series,
            order=(1, 1, 1),
            trend="c",
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        result = model.fit(disp=False)
    forecast = result.get_forecast(steps=horizon)
    conf = forecast.conf_int(alpha=0.2)
    future = pd.DataFrame(
        {
            "date": forecast.predicted_mean.index,
            "forecast_crore": forecast.predicted_mean.values,
            "lower_crore": conf.iloc[:, 0].values,
            "upper_crore": conf.iloc[:, 1].values,
        }
    )
    future["year"] = future["date"].dt.year
    return future

