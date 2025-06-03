import streamlit as st
from queries.visualization_queries import get_bubble_chart_data
from visualizations.borough_business_graph import plot_borough_bubble_chart
from connect import get_connection

if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
conn = st.session_state.conn

st.title("Borough Business Visualization Example")

# Compact select boxes on the same row
col1, col2, col3 = st.columns(3)
with col1:
    borough = st.selectbox("Select Borough", options=["Merton", "Havering", "Camden"], key="borough", label_visibility="collapsed")
    st.write("**Borough**")
with col2:
    year = st.selectbox("Select Year", options=[2020, 2021, 2022], key="year", label_visibility="collapsed")
    st.write("**Year**")
with col3:
    business_type = st.selectbox("Select Business Type", options=["pub", "restaurant", "fast_food"], key="business_type", label_visibility="collapsed")
    st.write("**Business Type**")

# Query data
data = get_bubble_chart_data(conn, borough, year, business_type)

# Collapsible data table
with st.expander("Show Queried Data Table"):
    st.dataframe(data)

# Plot
fig = plot_borough_bubble_chart(data)
st.plotly_chart(fig, use_container_width=True)
