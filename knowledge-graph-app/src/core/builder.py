import streamlit as st
from .schema_setup import create_constraints_and_indexes
from .data_importer import (
    import_business_data, 
    import_population_density_data,
    import_business_survival_rate_data
)
from .create_relationships import (
    connect_businesses_to_boroughs, 
    connect_boroughs_to_aggregate, 
    connect_neighbouring_boroughs
)


def build_knowledge_graph(conn, test_boroughs=[]):
    # TODO: when necessary, add more edges to make strongly connected graph for improved query runtimes  
    # reset the database
    clear_database(conn)

    # populate KG with nodes
    create_constraints_and_indexes(conn)
    import_business_data(conn, test_boroughs)
    import_population_density_data(conn, test_boroughs)
    import_business_survival_rate_data(conn, test_boroughs)

    # create relationships in KG
    connect_businesses_to_boroughs(conn, test_boroughs)
    connect_neighbouring_boroughs(conn, test_boroughs)
    connect_boroughs_to_aggregate(conn, test_boroughs)


def clear_database(conn):
    st.info("Clearing the database (detaching and deleting all nodes and relationships)...")
    query_delete_all = "MATCH (n) DETACH DELETE n"
    conn.query(query_delete_all)

    constraints = conn.query("SHOW CONSTRAINTS")
    for constraint in constraints[0]:
        name = constraint.get('name')
        drop_query = f"DROP CONSTRAINT {name} IF EXISTS"
        st.info(f"Dropping constraint: {name}")
        conn.query(drop_query)

    indexes = conn.query("SHOW INDEXES")
    for index in indexes[0]:
        name = index.get('name')
        drop_query = f"DROP INDEX {name} IF EXISTS"
        st.info(f"Dropping index: {name}")
        conn.query(drop_query)

    st.info("Database cleared.")
    