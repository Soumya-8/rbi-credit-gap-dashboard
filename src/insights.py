"""Rule-based executive insight generation."""

from __future__ import annotations

import pandas as pd

from src.analytics import aggregate_sector, aggregate_state, credit_gap, yoy_growth


def generate_insights(state_df: pd.DataFrame, sector_df: pd.DataFrame) -> list[str]:
    """Generate deterministic business insights from current filtered data."""
    insights: list[str] = []
    if state_df.empty or sector_df.empty:
        return ["No records match the selected filters."]

    state_agg = aggregate_state(state_df)
    latest_year = int(state_agg["year"].max())
    previous_year = latest_year - 1
    latest = state_agg[state_agg["year"] == latest_year]
    gap_df = credit_gap(latest)

    growth = yoy_growth(state_agg, ["state"], "credit_crore")
    latest_growth = growth[growth["year"] == latest_year].dropna(subset=["credit_crore_yoy_growth"])
    if not latest_growth.empty:
        fastest = latest_growth.nlargest(1, "credit_crore_yoy_growth").iloc[0]
        insights.append(
            f"{fastest['state']} recorded the fastest credit growth in {latest_year} "
            f"at {fastest['credit_crore_yoy_growth']:.1f}% year over year."
        )

    sector_agg = aggregate_sector(sector_df)
    latest_sector = sector_agg[sector_agg["year"] == latest_year]
    prev_sector = sector_agg[sector_agg["year"] == previous_year]
    if not latest_sector.empty:
        top_sector = latest_sector.nlargest(1, "credit_crore").iloc[0]
        insights.append(
            f"{top_sector['sector']} is the largest lending segment in {latest_year}, "
            f"with Rs {top_sector['credit_crore']:,.0f} crore in outstanding credit."
        )
    if not prev_sector.empty:
        merged = latest_sector.merge(prev_sector, on="sector", suffixes=("_latest", "_prev"))
        merged["growth"] = (
            (merged["credit_crore_latest"] - merged["credit_crore_prev"])
            / merged["credit_crore_prev"]
            * 100
        )
        strongest = merged.nlargest(1, "growth").iloc[0]
        weakest = merged.nsmallest(1, "growth").iloc[0]
        insights.append(
            f"{strongest['sector']} expanded the most among sectors, rising "
            f"{strongest['growth']:.1f}% over {previous_year}."
        )
        insights.append(
            f"{weakest['sector']} showed the weakest sector momentum, with "
            f"{weakest['growth']:.1f}% growth over {previous_year}."
        )

    underserved = gap_df.nlargest(1, "credit_gap_crore").iloc[0]
    overfinanced = gap_df.nsmallest(1, "credit_gap_crore").iloc[0]
    insights.append(
        f"{underserved['state']} has the largest estimated credit gap at "
        f"Rs {underserved['credit_gap_crore']:,.0f} crore, making it a priority opportunity market."
    )
    insights.append(
        f"{overfinanced['state']} is the most over-indexed market versus expected credit, "
        f"with a gap of Rs {overfinanced['credit_gap_crore']:,.0f} crore."
    )

    ratio_leader = latest.nlargest(1, "deposit_credit_ratio").iloc[0]
    ratio_laggard = latest.nsmallest(1, "deposit_credit_ratio").iloc[0]
    insights.append(
        f"{ratio_leader['state']} has the highest deposit-credit ratio "
        f"({ratio_leader['deposit_credit_ratio']:.1f}%), while {ratio_laggard['state']} "
        f"has the lowest ({ratio_laggard['deposit_credit_ratio']:.1f}%)."
    )
    return insights

