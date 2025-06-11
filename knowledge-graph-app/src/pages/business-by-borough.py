import streamlit as st
from queries.queries import (
    get_population_for_boroughs_in_range, get_years, get_borough_and_neighbours,
    get_population_for_boroughs, get_business_count_for_boroughs,
    get_business_survival_rates_for_boroughs, get_all_boroughs, get_all_business_types
)
from visualizations.borough_business_graph import plot_borough_scatter
from visualizations.bar_chart import plot_generic_barchart
from connect import get_connection
import pandas as pd


st.set_page_config(layout="wide")

if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
conn = st.session_state.conn

# Map sidebar keys to main keys for backward compatibility
borough = st.session_state.get("borough_sidebar", "Merton")
year = st.session_state.get("year_sidebar", 2020)
business_type = st.session_state.get("business_type_sidebar", "atm")

# ---- Retrieve Data ----
all_borough_names = get_all_boroughs(conn)
neighbour_borough_names = get_borough_and_neighbours(conn, borough)
# filter the boroughs to not use 'City of London', 'Inner London', 'Outer London'
all_borough_names = [b for b in all_borough_names if b not in ["City of London", "Inner London", "Outer London", "Greater London"]]
populations = get_population_for_boroughs(conn, all_borough_names, year)
business_counts = get_business_count_for_boroughs(conn, all_borough_names, business_type)

data1 = []
for b in all_borough_names:
    pop = populations.get(b, 0)
    bus = business_counts.get(b, 0)
    ratio = (pop / bus) if bus else 0  # per 10,000 people
    data1.append({
        "borough": b,
        "population": pop,
        "business_count": bus,
        "business_to_population_ratio": ratio,
    })

data2 = []
for b in neighbour_borough_names:
    pop = populations.get(b, 0)
    bus = business_counts.get(b, 0)
    ratio = (pop / bus) if bus else 0  # per 10,000 people
    data2.append({
        "borough": b,
        "population": pop,
        "business_count": bus,
        "business_to_population_ratio": ratio,
    })

st.subheader(f"Business Density and Population size ({year} - {business_type.capitalize()}s - {borough.capitalize()})")
fig2 = plot_borough_scatter(data1, borough)
st.plotly_chart(fig2, use_container_width=True)

# --- Growth Rate and Survival Rate Visualizations ---

# Get available years from the database
all_boroughs = get_all_boroughs(conn)
years = get_years(conn)
if years:
    min_year_db, max_year_db = min(years), max(years)
else:
    min_year_db, max_year_db = 1999, 2050
all_years = sorted(years) if years else list(range(1999, 2051))
all_business_types = get_all_business_types(conn)

# --- Sidebar sliders with synchronized middle year ---
with st.sidebar:
    st.subheader("Visualization Settings")
    borough = st.selectbox(
        "Select Borough", 
        options=all_boroughs,
        index=all_boroughs.index(borough) if borough in all_boroughs else 0,
        key="borough_sidebar"
    )
    year = st.selectbox(
        "Select Year", 
        options=all_years,
        index=all_years.index(year) if year in all_years else 0, 
        key="year_sidebar"
    )
    business_type = st.selectbox(
        "Select Business Type",
        options=all_business_types, 
        index=all_business_types.index(business_type) if business_type in all_business_types else 0,
        key="business_type_sidebar"
    )
    # Initialize session state for slider values
    if "start_year" not in st.session_state:
        st.session_state.start_year = 2006
    if "middle_year" not in st.session_state:
        st.session_state.middle_year = 2011
    if "end_year" not in st.session_state:
        st.session_state.end_year = 2016

    # First slider for start and middle year
    start_year, middle_year = st.slider(
        "Select Start and Middle Year for Growth Rate Calculation",
        min_value=all_years[0],
        max_value=all_years[-2],
        value=(st.session_state.start_year, st.session_state.middle_year),
        step=1,
        key="slider1"
    )
    # Second slider for middle and end year
    middle_year_2, end_year = st.slider(
        "Select Middle and End Year for Growth Rate Calculation",
        min_value=all_years[1],
        max_value=all_years[-1],
        value=(st.session_state.middle_year, st.session_state.end_year),
        step=1,
        key="slider2"
    )

    # --- Synchronize the middle year between sliders ---
    # If the user changes one slider, update the other
    if middle_year != st.session_state.middle_year:
        st.session_state.middle_year = middle_year
        st.session_state.end_year = end_year
    if middle_year_2 != st.session_state.middle_year:
        st.session_state.middle_year = middle_year_2
        st.session_state.start_year = start_year
    # Always keep both sliders in sync
    if middle_year != middle_year_2:
        # Set both to the most recently changed value
        st.session_state.middle_year = middle_year
        middle_year_2 = middle_year
    # Update session state for start and end
    st.session_state.start_year = start_year
    st.session_state.end_year = end_year

    # selectbox for survival rate options
    survival_rate_options = [
        "all",
        "one_year_rate",
        "two_year_rate",
        "three_year_rate",
        "four_year_rate",
        "five_year_rate"
    ]
    selected_survival_rate = st.selectbox(
        "Select Survival Rate(s) to Display",
        options=survival_rate_options,
        index=0  # default to 'all'
    )

# Use session state values for the rest of the code
start_year = st.session_state.start_year
middle_year = st.session_state.middle_year
end_year = st.session_state.end_year
middle_year_2 = st.session_state.middle_year

selected_years = [st.session_state.start_year, st.session_state.middle_year, st.session_state.end_year]
if st.session_state.middle_year != middle_year_2:
    st.warning("The middle year must be the same in both sliders. Adjust the sliders so the end of the first matches the start of the second.")
else:
    pop_data = get_population_for_boroughs_in_range(conn, neighbour_borough_names, st.session_state.start_year, st.session_state.end_year)
    pop_df = pd.DataFrame(pop_data, columns=['borough', 'year', 'population'])
    if not pop_df.empty:
        pop_df['year'] = pd.to_numeric(pop_df['year'], errors='coerce')
        pop_df['population'] = pd.to_numeric(pop_df['population'], errors='coerce')
        pop_df['borough'] = pop_df['borough'].astype(str)
        pop_df = pop_df[pop_df['year'].isin(selected_years)]
        pop_df = pop_df.dropna(subset=['year', 'population', 'borough'])
        pivot = pop_df.pivot(index='borough', columns='year', values='population')
        pivot = pivot.dropna(subset=selected_years, how='any')
        pivot['past_growth_rate'] = ((pivot[st.session_state.middle_year] - pivot[st.session_state.start_year]) / pivot[st.session_state.start_year]) * 100
        pivot['future_growth_rate'] = ((pivot[st.session_state.end_year] - pivot[st.session_state.middle_year]) / pivot[st.session_state.middle_year]) * 100
        growth_df = pivot[['past_growth_rate', 'future_growth_rate']].reset_index().melt(
            id_vars='borough',
            value_vars=['past_growth_rate', 'future_growth_rate'],
            var_name='period',
            value_name='growth_rate'
        )
        period_labels = {
            'past_growth_rate': f"{st.session_state.start_year}-{st.session_state.middle_year} (Past)",
            'future_growth_rate': f"{st.session_state.middle_year}-{st.session_state.end_year} (Projected)"
        }
        growth_df['period'] = growth_df['period'].map(period_labels)
    else:
        growth_df = pd.DataFrame(columns=['borough', 'period', 'growth_rate'])

    survival_data = get_business_survival_rates_for_boroughs(conn, neighbour_borough_names, st.session_state.middle_year)
    survival_df = pd.DataFrame(survival_data, columns=[
        "borough",
        "year",
        "businesses_started",
        "one_year_rate",
        "two_year_rate",
        "three_year_rate",
        "four_year_rate",
        "five_year_rate"
    ])

    # Ensure both dataframes are sorted by borough name for consistent y-axis
    borough_order = sorted(growth_df['borough'].unique()) if not growth_df.empty else []
    if not growth_df.empty:
        growth_df['borough'] = pd.Categorical(growth_df['borough'], categories=borough_order, ordered=True)
        growth_df = growth_df.sort_values('borough')
    if not survival_df.empty:
        survival_df['borough'] = pd.Categorical(survival_df['borough'], categories=borough_order, ordered=True)
        survival_df = survival_df.sort_values('borough')

    chart_col1, chart_col2 = st.columns([1, 1], gap="large")
    with chart_col1:
        st.subheader(f"Population Growth Rate by Borough for {borough} and neighbouring boroughs")
        if not growth_df.empty:
            fig_growth = plot_generic_barchart(
                growth_df,
                x_col="growth_rate",
                y_col="borough",
                color_col="period",
                title="",
                color_scheme="Set1",
                x_axis_label="Growth Rate (%)",
                y_axis_label="Borough",
                barmode="group",
            )
            fig_growth.update_layout(yaxis={'categoryorder':'array', 'categoryarray': borough_order})
            fig_growth.update_traces(orientation='h')
            st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("No growth rate data available for the selected boroughs and years.")
    with chart_col2:
        st.subheader(f"Business Survival Rate by Borough for {borough} and neighbouring boroughs ({st.session_state.middle_year})")
        if not survival_df.empty:
            period_labels = {
                'one_year_rate': '1 Year',
                'two_year_rate': '2 Years',
                'three_year_rate': '3 Years',
                'four_year_rate': '4 Years',
                'five_year_rate': '5 Years'
            }
            
            if selected_survival_rate == "all":
                value_vars = list(period_labels.keys())
            else:
                value_vars = [selected_survival_rate]

            survival_long = survival_df.melt(
                id_vars=['borough', 'year'],
                value_vars=value_vars,
                var_name='period',
                value_name='survival_rate'
            )
            survival_long['period'] = survival_long['period'].map(period_labels)
            
            # Set period order for correct bar order within group
            period_order = [period_labels[k] for k in value_vars]
            survival_long['period'] = pd.Categorical(survival_long['period'], categories=period_order, ordered=True)
            
            # Ensure borough order is consistent
            survival_long['borough'] = pd.Categorical(survival_long['borough'], categories=borough_order, ordered=True)
            survival_long = survival_long.sort_values(['borough', 'period'])
            fig_survival = plot_generic_barchart(
                survival_long,
                x_col="survival_rate",
                y_col="borough",
                color_col="period",
                title="",
                color_scheme="Set1",
                x_axis_label="Survival Rate (%)",
                y_axis_label="Borough",
                barmode="group",
            )
            fig_survival.update_layout(yaxis={'categoryorder':'array', 'categoryarray': borough_order})
            fig_survival.update_traces(orientation='h')
            st.plotly_chart(fig_survival, use_container_width=True)
        else:
            st.info("No business survival rate data available for the selected boroughs and year.")
