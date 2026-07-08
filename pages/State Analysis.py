"""State analysis dashboard page."""

from __future__ import annotations

import streamlit as st

from app import get_prepared_data, sidebar_filters
from src.analytics import aggregate_state, yoy_growth
from src.load_data import filter_dataframe
from src.utils import to_csv_download
from src.visualizations import bar_chart, india_choropleth, line_chart, scatter_bubble

st.set_page_config(page_title="State Analysis", layout="wide")
st.title("State Analysis")

state_df, sector_df, _ = get_prepared_data()
filters = sidebar_filters(state_df, sector_df)
state_filtered = filter_dataframe(state_df, **{k: v for k, v in filters.items() if k != "sectors"})

if state_filtered.empty:
    st.error("No state records match the current filters.")
    st.stop()

state_agg = aggregate_state(state_filtered)
latest = state_agg[state_agg["year"] == state_agg["year"].max()]
growth = yoy_growth(state_agg, ["state"], "credit_crore")

top10 = latest.nlargest(10, "credit_crore")
bottom10 = latest.nsmallest(10, "credit_crore")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(bar_chart(top10, "state", "credit_crore", "Top 10 States by Credit", color="region"), use_container_width=True)
with c2:
    st.plotly_chart(bar_chart(bottom10, "state", "credit_crore", "Bottom 10 States by Credit", color="region"), use_container_width=True)

st.plotly_chart(india_choropleth(latest, "credit_per_capita", "Credit Per Capita Map"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(line_chart(growth, "year", "credit_crore", "state", "State Credit Growth"), use_container_width=True)
with c4:
    st.plotly_chart(
        scatter_bubble(
            latest,
            "deposit_credit_ratio",
            "credit_per_capita",
            "credit_crore",
            "region",
            "state",
            "Deposit-Credit Ratio vs Credit Per Capita",
        ),
        use_container_width=True,
    )

table = latest.sort_values("credit_crore", ascending=False)
st.dataframe(table, use_container_width=True)
st.download_button("Export state analysis", to_csv_download(table), "state_analysis.csv", "text/csv")

