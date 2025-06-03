import streamlit as st
from connect import get_connection
from core.builder import build_knowledge_graph


if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
conn = st.session_state.conn
st.title("Bank Loan-Officer's Knowledge Graph - London Boroughs")

if st.sidebar.button("Build Knowledge Graph"):
    try:
        test_boroughs = []
        st.info("Building knowledge graph, this may take a while...")
        build_knowledge_graph(conn, test_boroughs)
        st.success("Knowledge graph build completed successfully!")
    except Exception as e:
        st.error(f"An error occurred during graph build: {e}")

st.sidebar.markdown("---")

preset_queries = {
    "Boroughs": "MATCH (b:Borough) RETURN b LIMIT 25",
    "Businesses": "MATCH (b:Business) RETURN b LIMIT 25",
    "Relationships": "MATCH (a)-[r]->(b)  RETURN a AS source, type(r) AS relation, b AS target  LIMIT 25"
}
selection = st.sidebar.selectbox("Choose a table", list(preset_queries.keys()))

if st.sidebar.button("Show"):
    query = preset_queries[selection]
    records, summary, keys = conn.query(query)

    if records:
        import pandas as pd
        data = [record.data() for record in records]
        flattened_data = []
        first_row = data[0] if data else {}

        if "source" in first_row and "target" in first_row and "relation" in first_row:
            for row in data:
                flat_row = {
                    "source": row["source"].get("name"),
                    "relation": row.get("relation"),
                    "target": row["target"].get("name")
                }
                flattened_data.append(flat_row)
        else:
            for row in data:
                for key, entity in row.items():
                    flattened_data.append(entity)
        df = pd.DataFrame(flattened_data)
        df = df.fillna("N/A")
        st.dataframe(df)
    else:
        st.warning("No results or query failed.")

st.sidebar.markdown("---")
