import streamlit as st
from visualizations.knowledge_graph import show_graph_view


def run_graph_query(query, parameters=None):
    """Run a Cypher query with optional parameters and display the graph."""
    conn = st.session_state.conn
    if parameters is None:
        parameters = {}
    records, _, _ = conn.query(query, parameters)
    if records:
        show_graph_view(records)
    else:
        st.warning("No relationships found to visualize.")


st.title("Graph View")

default_query = "MATCH (a)-[r]->(b) RETURN a AS source, type(r) AS relation, b AS target LIMIT 100"
query = st.text_area("Enter Cypher query for graph visualization:", value=default_query)
if st.button("Run Graph Query"):
    run_graph_query(query)