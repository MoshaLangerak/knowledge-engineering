import streamlit as st
import pandas as pd
from queries.queries import (
    get_all_boroughs, get_all_business_types, get_years,
    get_population_for_boroughs, get_business_count_for_boroughs, get_business_survival_rates_for_boroughs
)
from connect import get_connection
from visualizations.bar_chart import plot_distribution_barchart

st.set_page_config(layout="wide")

if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
conn = st.session_state.conn

st.title("Distribution Visualizations over Boroughs")

# --- Sidebar controls ---
all_boroughs = get_all_boroughs(conn)
all_business_types = get_all_business_types(conn)
all_years = get_years(conn)

st.sidebar.header("Visualization Settings")

dist_type = st.sidebar.radio(
    "Select Distribution to Visualize:",
    ["Business Density", "Survival Rate"]
)

# --- Business per Population Ratio Distribution ---
if dist_type == "Business Density":
    # Set default values for sidebar controls
    year = st.sidebar.selectbox("Select Year", options=all_years, index=all_years.index(2025) if 2025 in all_years else 0)
    business_type = st.sidebar.selectbox("Select Business Type", options=all_business_types)
    highlight_borough = st.sidebar.selectbox("Highlight Borough", options=all_boroughs, 
                                             index=all_boroughs.index("Merton") if "Merton" in all_boroughs else 0)
    bin_mode = st.sidebar.radio("Binning Mode", ["Quantile", "Range"], index=0)
    n_bins = st.sidebar.slider("Number of Bins", min_value=5, max_value=20, value=10)

    # Get data
    populations = get_population_for_boroughs(conn, all_boroughs, year)
    business_counts = get_business_count_for_boroughs(conn, all_boroughs, business_type)
    data = []
    for b in all_boroughs:
        pop = populations.get(b, 0)
        bus = business_counts.get(b, 0)
        ratio = (bus / pop * 10000) if pop else 0
        data.append({"borough": b, "business_to_population_ratio": ratio})
    ratios = [d["business_to_population_ratio"] for d in data]
    highlight_value = next((d["business_to_population_ratio"] for d in data if d["borough"] == highlight_borough), None)
    st.subheader(f"Distribution of Business Density ({business_type}, {year})")
    
    fig = plot_distribution_barchart(
        ratios,
        item_value=highlight_value,
        n_bins=n_bins,
        quantile_binning=(bin_mode == "Quantile"),
        x_label="Businesses per 10,000 people",
        y_label="Number of Boroughs",
        title=f"Distribution of Business/Population Ratio ({business_type}, {year})"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Highlighted: {highlight_borough} ({highlight_value:.2f} businesses per 10,000 people)")

# --- Survival Rate Distribution ---
else:
    year = st.sidebar.selectbox("Select Year", options=all_years, index=all_years.index(2025) if 2025 in all_years else 0)
    survival_period_options = [
        ("one_year_rate", "1 Year Survival Rate"),
        ("two_year_rate", "2 Year Survival Rate"),
        ("three_year_rate", "3 Year Survival Rate"),
        ("four_year_rate", "4 Year Survival Rate"),
        ("five_year_rate", "5 Year Survival Rate")
    ]
    period_key, period_label = st.sidebar.selectbox(
        "Select Survival Rate Period",
        options=survival_period_options,
        format_func=lambda x: x[1],
        index=0
    )
    highlight_borough = st.sidebar.selectbox("Highlight Borough", options=all_boroughs, index=all_boroughs.index("Merton") if "Merton" in all_boroughs else 0)
    # Get data for all boroughs
    survival_data = get_business_survival_rates_for_boroughs(conn, all_boroughs, year)
    survival_df = pd.DataFrame(survival_data)
    rates = survival_df[period_key].dropna().tolist() if period_key in survival_df else []
    highlight_value = None
    if period_key in survival_df and highlight_borough in survival_df['borough'].values:
        highlight_value = survival_df.loc[survival_df['borough'] == highlight_borough, period_key].values[0]
    st.subheader(f"Distribution of {period_label} ({year})")
    bin_mode = st.sidebar.radio("Binning Mode", ["Quantile", "Range"], index=0)
    n_bins = st.sidebar.slider("Number of Bins", min_value=5, max_value=20, value=10)
    fig = plot_distribution_barchart(
        rates,
        item_value=highlight_value,
        n_bins=n_bins,
        quantile_binning=(bin_mode == "Quantile"),
        x_label=period_label,
        y_label="Number of Boroughs",
        title=f"Distribution of {period_label} ({year})"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Highlighted: {highlight_borough} ({highlight_value:.2f}%)" if highlight_value is not None else f"No data for {highlight_borough}")
