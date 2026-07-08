"""Executive insights dashboard page."""

from __future__ import annotations

import streamlit as st

from app import get_prepared_data, sidebar_filters
from src.analytics import aggregate_state, credit_gap
from src.insights import generate_insights
from src.load_data import filter_dataframe
from src.visualizations import bar_chart, scatter_bubble

st.set_page_config(page_title="Executive Insights", layout="wide")
st.title("Executive Insights")

state_df, sector_df, _ = get_prepared_data()
filters = sidebar_filters(state_df, sector_df)
state_filtered = filter_dataframe(state_df, **{k: v for k, v in filters.items() if k != "sectors"})
sector_filtered = filter_dataframe(sector_df, **filters)

if state_filtered.empty or sector_filtered.empty:
    st.error("No records match the current filters.")
    st.stop()

for insight in generate_insights(state_filtered, sector_filtered):
    st.success(insight)

latest = aggregate_state(state_filtered)
latest = latest[latest["year"] == latest["year"].max()]
gap = credit_gap(latest)
gap["gap_abs_crore"] = gap["credit_gap_crore"].abs().clip(lower=1)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(bar_chart(gap.nlargest(8, "opportunity_index"), "state", "opportunity_index", "Opportunity Index Leaders", color="region"), use_container_width=True)
with c2:
    st.plotly_chart(
        scatter_bubble(
            gap,
            "priority_sector_share",
            "gap_pct",
            "gap_abs_crore",
            "region",
            "state",
            "Priority Sector Share vs Credit Gap",
        ),
        use_container_width=True,
    )

