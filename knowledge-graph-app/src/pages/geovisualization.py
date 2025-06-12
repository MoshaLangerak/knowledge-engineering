import streamlit as st
from connect import get_connection
from core.data_importer import import_borough_shapes
from streamlit_folium import st_folium
from queries.queries import (
    get_business_types, 
    get_years
)
from visualizations.greater_london_map import (
    compute_ratio_dataframe, 
    plot_interactive_map
)

st.set_page_config(layout="wide")

if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
    
conn = st.session_state.conn

# Keep track of the state of the items on the page
if "map_data" not in st.session_state:
    st.session_state.map_data = None
if "ratio_gdf" not in st.session_state:
    st.session_state.ratio_gdf = None
if "last_business_type" not in st.session_state:
    st.session_state.last_business_type = None
if "last_year" not in st.session_state:
    st.session_state.last_year = None

business_types = get_business_types(conn)
years = get_years(conn)

with st.sidebar:
    business_type = st.selectbox("Choose a business type:", business_types)
    year = st.selectbox("Select a population year:", years)

    inputs_changed = (
        st.session_state.last_business_type != business_type
        or st.session_state.last_year != year
    )

st.header(f"Geographic View of People to {business_type} Business Ratio in {year}")

# If business type or year input has changed, than the map is rendered again. 
if inputs_changed:
    try:
        gdf = import_borough_shapes()
        st.session_state.ratio_gdf = compute_ratio_dataframe(conn, gdf, business_type, year)
        st.session_state.map_data = plot_interactive_map(
            st.session_state.ratio_gdf, 
            business_type, 
            year
        )
        st.session_state.last_business_type = business_type
        st.session_state.last_year = year
    except Exception as e:
        st.error(f"Error generating map: {str(e)}")

# Check if any boroughs miss people per business data. If so, inform the user on the interface
if st.session_state.ratio_gdf is not None:
    missing_data = st.session_state.ratio_gdf[
        st.session_state.ratio_gdf['people_per_business'].isnull()
    ]
    
    if len(missing_data) > 0:
        missing_boroughs = missing_data['borough'].tolist()
        message = (
            f"Missing data for: {missing_boroughs[0]}" if len(missing_boroughs) == 1
            else "Missing data for: " + ", ".join(missing_boroughs[:-1]) + f" and {missing_boroughs[-1]}"
        )
        # st.warning(message)

# Display the map
if st.session_state.map_data is not None:
    st_folium(
        st.session_state.map_data, 
        width=None,  
        height=800, 
        key="static_map",
        returned_objects=[]  
    )
    
st.write("Click on borough to see the people per business ratio.")
