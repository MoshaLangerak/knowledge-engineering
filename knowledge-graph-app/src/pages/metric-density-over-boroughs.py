import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from queries.queries import (
    get_all_boroughs, get_all_business_types, get_years,
    get_population_for_boroughs, get_business_count_for_boroughs,
    get_business_survival_rates_for_boroughs,
    get_survival_years
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
survival_years = get_survival_years(conn)

st.sidebar.header("Visualization Settings")

dist_type = st.sidebar.radio(
    "Select Distribution to Visualize:",
    ["Business Density", "Survival Rates"]
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
        title=f"Distribution of {business_type} Density in {year}"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Highlighted: {highlight_borough} ({highlight_value:.2f} {business_type}s per 10,000 people)")

else:
    year = st.sidebar.selectbox("Select Year", options=survival_years, index=survival_years.index(2016) if 2016 in survival_years else 0)
    highlight_borough = st.sidebar.selectbox("Highlight Borough", options=all_boroughs, 
                                             index=all_boroughs.index("Merton") if "Merton" in all_boroughs else 0)
    # Get data for all boroughs
    survival_data = get_business_survival_rates_for_boroughs(conn, all_boroughs, year)
    survival_df = pd.DataFrame(survival_data, columns=[
        'borough', 'year', 'businesses_started', 'one_year_rate', 'two_year_rate', 'three_year_rate', 'four_year_rate', 'five_year_rate'
    ])
    
    periods = [
        ("one_year_rate", "1 Year Survival Rate"),
        ("two_year_rate", "2 Year Survival Rate"),
        ("three_year_rate", "3 Year Survival Rate"),
        ("four_year_rate", "4 Year Survival Rate"),
        ("five_year_rate", "5 Year Survival Rate")
    ]
    
    st.subheader(f"Survival Rate Ranges and Borough Ranking ({year})")
    fig = go.Figure()
    box_width = 0.5
    marker_size = 12
    for i, (period_key, period_label) in enumerate(periods):
        rates = survival_df[period_key].dropna()
        if len(rates) == 0:
            continue
        # Boxplot for all boroughs
        fig.add_trace(go.Box(
            y=rates,
            x=[period_label]*len(rates),
            name=period_label,
            boxpoints=False,
            marker_color='lightblue',
            width=box_width,
            showlegend=False
        ))
        # Mark selected borough
        if period_key in survival_df and highlight_borough in survival_df['borough'].values:
            borough_value = survival_df.loc[survival_df['borough'] == highlight_borough, period_key].values[0]
            # Calculate ranking (1 = best)
            rank = (rates > borough_value).sum() + 1
            fig.add_trace(go.Scatter(
                x=[period_label],
                y=[borough_value],
                mode='markers+text',
                marker=dict(color='crimson', size=marker_size, symbol='diamond'),
                text=[f"{highlight_borough}<br>Rank: {rank}/{len(rates)}"],
                textposition="top center",
                showlegend=False
            ))
    fig.update_layout(
        yaxis_title="Survival Rate (%)",
        xaxis_title="Survival Period",
        title=f"Business Survival Rate Ranges and {highlight_borough} Ranking ({year})",
        boxmode='group',
        template='plotly_white',
        xaxis=dict(type='category'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
