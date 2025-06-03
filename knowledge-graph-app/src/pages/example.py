import streamlit as st
from queries.visualization_queries import get_visualization_data
from visualizations.borough_business_graph import plot_borough_business_graph
from connect import get_connection

if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
conn = st.session_state.conn

st.title("Borough Business Visualization Example")
conn = st.session_state.conn
# User input widgets
borough = st.selectbox("Select Borough", options=["Camden", "Havering", "Merton"])  # TODO: replace with dynamic list
year = st.selectbox("Select Year", options=[2020, 2021, 2022])  # TODO: replace with dynamic list
business_type = st.selectbox("Select Business Type", options=["pub", "restaurant", "fast_food"])  # TODO: replace with dynamic list

# Query data
data = get_visualization_data(conn, borough, year, business_type)

# Print data as a table for debugging
st.subheader("Queried Data Table")
st.dataframe(data)

# Plot
fig = plot_borough_business_graph(data, borough)
st.plotly_chart(fig, use_container_width=True)
