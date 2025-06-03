import streamlit as st


def create_constraints_and_indexes(conn):
    """
    Defines and creates constraints and indexes for the knowledge graph.
    This function should be idempotent (safe to run multiple times).
    """
    st.info("Setting up constraints and indexes...")

    # TODO: think of more constraints and indexes
    business_id_constraint = "CREATE CONSTRAINT business_unique_id IF NOT EXISTS FOR (b:Business) REQUIRE b.businessId IS UNIQUE"

    queries = [
        business_id_constraint
    ]

    for query in queries:
        st.info(f"Executing: {query}")
        conn.query(query)

    st.info("Constraints and indexes setup complete.")
