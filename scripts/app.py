import streamlit as st
import pandas as pd
from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Initialize Neo4j connection
def get_connection():
    return Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

conn = get_connection()

st.title("Neo4j Query Explorer")

# Sidebar: Select or enter Cypher query
preset_queries = {
    "Find all nodes": "MATCH (n) RETURN n LIMIT 25",
    "Find people": "MATCH (p:Person) RETURN p.name AS name LIMIT 25",
    "Count nodes": "MATCH (n) RETURN count(n) AS node_count"
}
selection = st.sidebar.selectbox("Choose a preset query", list(preset_queries.keys()))
custom_query = st.sidebar.text_area("Or enter a custom Cypher query", height=100)

# Run query

if st.sidebar.button("Run Query"):
    query = custom_query if custom_query.strip() else preset_queries[selection]
    records, summary, keys = conn.query(query)
    
    if records:
        # Convert Neo4j records to DataFrame
        data = [record.data() for record in records]
        df = pd.DataFrame(data)
        st.write("### Query Results")
        st.dataframe(df)
    else:
        st.warning("No results or query failed.")
