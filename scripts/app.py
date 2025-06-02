import streamlit as st
import pandas as pd
from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from main import build_knowledge_graph

# Initialize Neo4j connection
def get_connection():
    return Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

conn = get_connection()

st.title("Neo4j Query Explorer")

# Button to build the knowledge graph
if st.button("Build Knowledge Graph"):
    try:
        build_knowledge_graph()
        st.success("Knowledge graph build completed successfully!")
    except Exception as e:
        st.error(f"An error occurred during graph build: {e}")

# Sidebar: Select or enter Cypher query
preset_queries = {
    "Find all boroughs": "MATCH (b:Borough) RETURN b LIMIT 25",
    "Find all businesses": "MATCH (b:Business) RETURN b LIMIT 25",
    "Find all relationships": "MATCH (a)-[r]->(b)  RETURN a AS source, type(r) AS relation, b AS target  LIMIT 25"
}
selection = st.sidebar.selectbox("Choose a preset query", list(preset_queries.keys()))
custom_query = st.sidebar.text_area("Or enter a custom Cypher query", height=100)

# Run query
if st.sidebar.button("Run Query"):
    query = custom_query if custom_query.strip() else preset_queries[selection]
    records, summary, keys = conn.query(query)

    if records:
        data = [record.data() for record in records]
        flattened_data = []
        first_row = data[0] if data else {}

        if "source" in first_row and "target" in first_row and "relation" in first_row:
            # Handle relationship result
            for row in data:
                flat_row = {
                    "source": row["source"].get("name"),
                    "relation": row.get("relation"),
                    "target": row["target"].get("name")
                }
                flattened_data.append(flat_row)
        else:
            # Handle entity result
            for row in data:
                for key, entity in row.items():
                    flattened_data.append(entity)
                        
        df = pd.DataFrame(flattened_data)
        df = df.fillna("N/A")
        st.dataframe(df)          
        
    else:
        st.warning("No results or query failed.")


# Examples of relationship and entity records returned by neo4j
# {'source': {'osmId': 25496840, 'name': '26 Furnival Street', 'type': 'pub'}, 'relation': 'LOCATED_IN', 'target': {'mid_year_estimate_1988': 6200, 'projection_2031': 10843, 'projection_2021': 9559, 'name': 'City of London', 'mid_year_estimate_1939': 9000, 'projection_2015': 8101, 'census_2011': 7375, 'projection_2039': 11623}}
# {'b': {'mid_year_estimate_1988': 6200, 'projection_2031': 10843, 'projection_2021': 9559, 'name': 'City of London', 'mid_year_estimate_1939': 9000, 'projection_2015': 8101, 'census_2011': 7375, 'projection_2039': 11623}}
