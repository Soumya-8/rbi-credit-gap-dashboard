"""Streamlit entry point for the RBI Credit Gap Dashboard."""

from __future__ import annotations

import streamlit as st

from config import APP_SUBTITLE, APP_TITLE
from src.analytics import aggregate_state, national_kpis
from src.database import initialize_database
from src.insights import generate_insights
from src.load_data import filter_dataframe, load_dashboard_data
from src.preprocessing import prepare_sector_data, prepare_state_data
from src.utils import format_inr_crore, normalize_selection, to_csv_download
from src.visualizations import india_choropleth, line_chart, stacked_bar


@st.cache_data(show_spinner=False)
def get_prepared_data():
    """Load and prepare app datasets."""
    data = load_dashboard_data()
    return (
        prepare_state_data(data.state),
        prepare_sector_data(data.sector),
        data.deposit,
    )


def sidebar_filters(state_df, sector_df):
    """Render global sidebar filters."""
    st.sidebar.title("Filters")
    min_year, max_year = int(state_df["year"].min()), int(state_df["year"].max())
    years = st.sidebar.slider("Year range", min_year, max_year, (min_year, max_year))
    sectors = st.sidebar.multiselect("Sector", ["All"] + sorted(sector_df["sector"].unique()), default=["All"])
    states = st.sidebar.multiselect("State", ["All"] + sorted(state_df["state"].unique()), default=["All"])
    bank_types = st.sidebar.multiselect("Bank type", ["All"] + sorted(state_df["bank_type"].unique()), default=["All"])
    regions = st.sidebar.multiselect("Region", ["All"] + sorted(state_df["region"].unique()), default=["All"])
    search = st.sidebar.text_input("Search", placeholder="State, sector, region, bank")
    return {
        "years": years,
        "sectors": normalize_selection(sectors),
        "states": normalize_selection(states),
        "bank_types": normalize_selection(bank_types),
        "regions": normalize_selection(regions),
        "search": search.strip() or None,
    }


def kpi_card(label: str, value: str, help_text: str | None = None) -> None:
    """Render a metric card."""
    st.metric(label=label, value=value, help=help_text)


def main() -> None:
    """Render the dashboard overview page."""
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    with st.spinner("Loading RBI-style banking datasets..."):
        state_df, sector_df, deposit_df = get_prepared_data()

    filters = sidebar_filters(state_df, sector_df)
    state_filtered = filter_dataframe(state_df, **{k: v for k, v in filters.items() if k != "sectors"})
    sector_filtered = filter_dataframe(sector_df, **filters)

    if state_filtered.empty or sector_filtered.empty:
        st.error("No data matches the current filters. Please broaden the selection.")
        st.stop()

    if st.sidebar.button("Initialize SQLite database"):
        db_path = initialize_database(state_filtered, sector_filtered, deposit_df)
        st.sidebar.success(f"SQLite database updated: {db_path.name}")

    kpis = national_kpis(state_filtered, sector_filtered)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Credit", format_inr_crore(kpis["total_credit"]))
    c2.metric("Total Deposits", format_inr_crore(kpis["total_deposits"]))
    c3.metric("Avg Credit Growth", f"{kpis['avg_credit_growth']:.1f}%")
    c4.metric("Top Lending Sector", str(kpis["top_sector"]))
    c5.metric("Highest Credit State", str(kpis["highest_credit_state"]))

    state_agg = aggregate_state(state_filtered)
    yearly = state_agg.groupby("year", as_index=False)[["credit_crore", "deposits_crore"]].sum()
    latest = state_agg[state_agg["year"] == state_agg["year"].max()]
    sector_yearly = sector_filtered.groupby(["year", "sector"], as_index=False)["credit_crore"].sum()

    left, right = st.columns([1.15, 0.85])
    with left:
        st.plotly_chart(
            line_chart(
                yearly,
                "year",
                "credit_crore",
                None,
                "National Credit Trend",
                {"credit_crore": "Credit (crore)", "year": "Year"},
            ),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(india_choropleth(latest, "credit_crore", "National Credit Map"), use_container_width=True)

    st.plotly_chart(
        stacked_bar(sector_yearly, "year", "credit_crore", "sector", "Sector-wise Credit Deployment"),
        use_container_width=True,
    )

    st.subheader("Executive Signals")
    for insight in generate_insights(state_filtered, sector_filtered)[:4]:
        st.info(insight)

    st.download_button(
        "Export filtered state data",
        data=to_csv_download(state_filtered),
        file_name="filtered_state_credit.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
