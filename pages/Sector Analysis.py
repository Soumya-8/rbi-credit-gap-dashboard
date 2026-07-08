"""Sector analysis dashboard page."""

from __future__ import annotations

import streamlit as st

from app import get_prepared_data, sidebar_filters
from src.analytics import aggregate_sector, yoy_growth
from src.load_data import filter_dataframe
from src.utils import to_csv_download
from src.visualizations import bar_chart, heatmap, line_chart, pie_chart, treemap

st.set_page_config(page_title="Sector Analysis", layout="wide")
st.title("Sector Analysis")

state_df, sector_df, _ = get_prepared_data()
filters = sidebar_filters(state_df, sector_df)
filtered = filter_dataframe(sector_df, **filters)

if filtered.empty:
    st.error("No sector records match the current filters.")
    st.stop()

sector_year = aggregate_sector(filtered)
latest_year = int(sector_year["year"].max())
latest = sector_year[sector_year["year"] == latest_year]
growth = yoy_growth(sector_year, ["sector"], "credit_crore")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(bar_chart(latest, "sector", "credit_crore", "Sector-wise Lending", color="sector"), use_container_width=True)
with c2:
    st.plotly_chart(pie_chart(latest, "sector", "credit_crore", "Credit Share by Sector"), use_container_width=True)

st.plotly_chart(line_chart(growth, "year", "credit_crore", "sector", "Sector Credit Growth Over Years"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    region_sector = filtered.groupby(["region", "sector"], as_index=False)["credit_crore"].sum()
    st.plotly_chart(heatmap(region_sector, "sector", "region", "credit_crore", "Regional Sector Heatmap"), use_container_width=True)
with c4:
    tree = filtered.groupby(["priority_classification", "sector"], as_index=False)["credit_crore"].sum()
    st.plotly_chart(treemap(tree, ["priority_classification", "sector"], "credit_crore", "Priority vs Non-priority Treemap"), use_container_width=True)

ranking = latest.sort_values("credit_crore", ascending=False).reset_index(drop=True)
ranking.index = ranking.index + 1
st.dataframe(ranking, use_container_width=True)
st.download_button("Export sector ranking", to_csv_download(ranking), "sector_ranking.csv", "text/csv")

