"""Credit gap analysis dashboard page."""

from __future__ import annotations

import streamlit as st

from app import get_prepared_data, sidebar_filters
from src.analytics import aggregate_state, credit_gap
from src.load_data import filter_dataframe
from src.utils import format_inr_crore, to_csv_download
from src.visualizations import bar_chart, scatter_bubble

st.set_page_config(page_title="Credit Gap Analysis", layout="wide")
st.title("Credit Gap Analysis")
st.caption("Expected credit is benchmarked against deposits, state development proxy, and regional lending capacity.")

state_df, sector_df, _ = get_prepared_data()
filters = sidebar_filters(state_df, sector_df)
state_filtered = filter_dataframe(state_df, **{k: v for k, v in filters.items() if k != "sectors"})

if state_filtered.empty:
    st.error("No state records match the current filters.")
    st.stop()

state_agg = aggregate_state(state_filtered)
latest = state_agg[state_agg["year"] == state_agg["year"].max()]
gap = credit_gap(latest).sort_values("credit_gap_crore", ascending=False)
gap["gap_abs_crore"] = gap["credit_gap_crore"].abs().clip(lower=1)

underfinanced = gap[gap["credit_gap_crore"] > 0]
overfinanced = gap[gap["credit_gap_crore"] < 0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Estimated Gap", format_inr_crore(underfinanced["credit_gap_crore"].sum()))
c2.metric("Underfinanced States", f"{len(underfinanced)}")
c3.metric("Overfinanced States", f"{len(overfinanced)}")
c4.metric("Max Opportunity Index", f"{gap['opportunity_index'].max():.1f}")

left, right = st.columns(2)
with left:
    st.plotly_chart(
        bar_chart(gap.head(12), "state", "credit_gap_crore", "Largest Credit Gaps", color="region"),
        use_container_width=True,
    )
with right:
    st.plotly_chart(
        scatter_bubble(
            gap,
            "credit_crore",
            "expected_credit_crore",
            "opportunity_index",
            "region",
            "state",
            "Actual vs Expected Credit",
        ),
        use_container_width=True,
    )

st.plotly_chart(
        scatter_bubble(
        gap,
        "deposit_credit_ratio",
        "gap_pct",
        "gap_abs_crore",
        "region",
        "state",
        "Credit Gap % vs Deposit-Credit Ratio",
    ),
    use_container_width=True,
)

display = gap[
    [
        "gap_rank",
        "state",
        "region",
        "credit_crore",
        "expected_credit_crore",
        "credit_gap_crore",
        "gap_pct",
        "deposit_credit_ratio",
        "opportunity_index",
    ]
]
display = display.reset_index(drop=True)
display.index = display.index + 1
st.dataframe(display, use_container_width=True)
st.download_button("Export credit gap table", to_csv_download(display), "credit_gap_analysis.csv", "text/csv")
