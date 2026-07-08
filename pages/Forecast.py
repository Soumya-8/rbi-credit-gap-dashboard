"""Forecast dashboard page."""

from __future__ import annotations

import streamlit as st

from app import get_prepared_data, sidebar_filters
from src.forecasting import build_timeseries, forecast_credit
from src.load_data import filter_dataframe
from src.preprocessing import merge_state_sector
from src.utils import to_csv_download
from src.visualizations import forecast_chart

st.set_page_config(page_title="Forecast", layout="wide")
st.title("Credit Forecast")

state_df, sector_df, _ = get_prepared_data()
filters = sidebar_filters(state_df, sector_df)
state_filtered = filter_dataframe(state_df, **{k: v for k, v in filters.items() if k != "sectors"})
sector_filtered = filter_dataframe(sector_df, **filters)

model_base = merge_state_sector(state_filtered, sector_filtered)
sectors = ["All"] + sorted(model_base["sector"].unique())
states = ["All"] + sorted(model_base["state"].unique())
c1, c2, c3 = st.columns(3)
sector = c1.selectbox("Forecast sector", sectors)
state = c2.selectbox("Forecast state", states)
horizon = c3.slider("Forecast horizon (years)", 1, 8, 4)

selected_sector = None if sector == "All" else sector
selected_state = None if state == "All" else state
ts = build_timeseries(model_base, sector=selected_sector, state=selected_state)

try:
    forecast = forecast_credit(ts, horizon=horizon)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.plotly_chart(forecast_chart(ts, forecast), use_container_width=True)
st.dataframe(forecast, use_container_width=True)
st.download_button("Export forecast", to_csv_download(forecast), "credit_forecast.csv", "text/csv")

