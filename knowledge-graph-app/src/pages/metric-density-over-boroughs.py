import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

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
    n_bins = st.sidebar.slider("Number of Bins", min_value=5, max_value=20, value=15)

    # Get data
    populations = get_population_for_boroughs(conn, all_boroughs, year)
    business_counts = get_business_count_for_boroughs(conn, all_boroughs, business_type)
    data = []
    for b in all_boroughs:
        pop = populations.get(b, 0)
        bus = business_counts.get(b, 0)
        ratio = pop / bus if bus else 0
        data.append({"borough": b, "population_to_business_ratio": ratio})
    ratios = [d["population_to_business_ratio"] for d in data]
    highlight_value = next((d["population_to_business_ratio"] for d in data if d["borough"] == highlight_borough), None)
    st.subheader(f"Distribution of People to Business Ratio ({business_type}, {year})")
    
    fig = plot_distribution_barchart(
        ratios,
        item_value=highlight_value,
        n_bins=n_bins,
        quantile_binning=False,
        x_label="People per Business Ratio",
        y_label="Number of Boroughs",
        title=f"Distribution of People to {business_type} Business Ratio in {year}"
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

# --- Visualisation 1: Comparison of Business Density Distributions ---
st.markdown("---")
st.subheader("Comparison of Business Density Distributions")

# Sidebar multiselect for the new comparison plot
selected_business_types = st.sidebar.multiselect(
    "Select up to 5 business types for comparison",
    options=all_business_types,
    default=all_business_types[:5] if len(all_business_types) >= 5 else all_business_types,
    max_selections=5
)

if selected_business_types:
    # We can reuse the `populations` data fetched earlier for the same year
    comparison_data = []
    for b_type in selected_business_types:
        business_counts_comp = get_business_count_for_boroughs(conn, all_boroughs, b_type)
        for b in all_boroughs:
            pop = populations.get(b, 0)
            bus = business_counts_comp.get(b, 0)
            # Only include valid ratios
            if bus and pop:
                ratio = pop / bus
                comparison_data.append({"business_type": b_type, "ratio": ratio})

    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        # Create a box plot to show the distribution for each business type
        fig_box = px.box(
            df_comparison,
            x="business_type",
            y="ratio",
            color="business_type",
            title=f"Distribution of People-to-Business Ratios in {year}",
            labels={
                "business_type": "Business Type",
                "ratio": "People per Business Ratio"
            },
            notched=False # Adds a notch to show confidence interval around the median
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("The box plot shows the distribution of the people-to-business ratio across all boroughs for the selected business types. The line in the middle of each box is the median.")

        # --- Visualization 1: Density Plot ---
        st.markdown("---")
        st.subheader("Smoothed Distribution of Business Density")

        # Clip the data at the 95th percentile to handle the long tail
        p95 = df_comparison['ratio'].quantile(0.95)
        df_clipped = df_comparison[df_comparison['ratio'] <= p95]

        # Prepare data for the distplot
        hist_data = [df_clipped[df_clipped['business_type'] == b_type]['ratio'] for b_type in selected_business_types]
        group_labels = selected_business_types

        # Create the density plot
        fig_dist = ff.create_distplot(
            hist_data,
            group_labels,
            show_hist=False,  # Only show the smoothed line
            show_rug=False    # Hide the rug plot for a cleaner look
        )
        fig_dist.update_layout(
            title_text='Density Plot of People-to-Business Ratios',
            xaxis_title='People per Business Ratio',
            yaxis_title='Density'
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.caption("This plot shows the smoothed probability density of the people-to-business ratio. Peaks in the lines indicate where the ratio is most common for a given business type.")

        # --- Visualization 2: Grouped Histogram (replaces Density Plot) ---
        st.markdown("---")
        st.subheader("Histogram of Business Density (Focused View)")

        # Clip the data at the 95th percentile to handle the long tail
        p95 = df_comparison['ratio'].quantile(0.95)
        df_clipped = df_comparison[df_comparison['ratio'] <= p95]

        st.info(f"Note: To improve readability, the histogram below is focused on the data up to the 95th percentile (ratio ≤ {p95:,.0f}). The box plot above shows the full data range.")

        # Add a slider to control the number of bins
        n_bins_hist = st.slider("Number of Bins for Histogram", min_value=5, max_value=50, value=20)

        if not df_clipped.empty:
            fig_hist = go.Figure()
            for b_type in selected_business_types:
                ratios = df_clipped[df_clipped['business_type'] == b_type]['ratio']
                if not ratios.empty:
                    fig_hist.add_trace(go.Histogram(
                        x=ratios,
                        name=b_type,
                        nbinsx=n_bins_hist
                    ))

            # Update layout for a grouped histogram
            fig_hist.update_layout(
                barmode='group',
                title_text='Histogram of People-to-Business Ratios',
                xaxis_title_text='People per Business Ratio',
                yaxis_title_text='Number of Boroughs',
                legend_title_text='Business Type'
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            st.caption("This histogram shows the distribution of the people-to-business ratio, counting the number of boroughs in each ratio bin.")
    else:
        st.warning("No data available for the selected business types to create a comparison plot.")
else:
    st.info("Select one or more business types from the sidebar to see a comparison of their distributions.")