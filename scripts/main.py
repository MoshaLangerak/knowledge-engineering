from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from schema_setup import create_constraints_and_indexes
from data_importer import (
    import_business_data, 
    import_population_density_data,
    import_business_survival_rate_data
)
from create_relationships import (
    connect_businesses_to_boroughs, 
    connect_boroughs_to_aggregate, 
    connect_neighbouring_boroughs
)


def build_knowledge_graph(st=None, test_boroughs=[]):
    if st is None:
        def st_print(msg): print(msg)
    else:
        st_print = st.info

    st_print("Starting knowledge graph build process...")
    conn = None
    try:
        conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        st_print("Successfully connected to Neo4j!")

        if not conn._Neo4jConnection__driver:
            st_print("Failed to connect to Neo4j. Aborting build.")
            return

        # TODO: when necessary, add more edges to make strongly connected graph for improved query runtimes  

        clear_database(conn, st_print=st_print)

        # populate KG with nodes
        create_constraints_and_indexes(conn, st_print=st_print)
        import_business_data(conn, test_boroughs=test_boroughs, st_print=st_print)
        import_population_density_data(conn, test_boroughs=test_boroughs, st_print=st_print)
        import_business_survival_rate_data(conn, test_boroughs=test_boroughs, st_print=st_print)

        # create relationships in KG
        connect_businesses_to_boroughs(conn, test_boroughs=test_boroughs, st_print=st_print)
        connect_neighbouring_boroughs(conn, st_print=st_print)
        connect_boroughs_to_aggregate(conn, st_print=st_print)

        st_print("Knowledge graph build process completed successfully!")

    except Exception as e:
        st_print(f"An error occurred during the build process: {e}")
    finally:
        if conn:
            conn.close()

def clear_database(conn: Neo4jConnection, st_print=print):
    st_print("Clearing the database (detaching and deleting all nodes and relationships)...")
    query_delete_all = "MATCH (n) DETACH DELETE n"
    conn.query(query_delete_all)

    constraints = conn.query("SHOW CONSTRAINTS")
    for constraint in constraints[0]:
        name = constraint.get('name')
        drop_query = f"DROP CONSTRAINT {name} IF EXISTS"
        st_print(f"Dropping constraint: {name}")
        conn.query(drop_query)

    indexes = conn.query("SHOW INDEXES")
    for index in indexes[0]:
        name = index.get('name')
        drop_query = f"DROP INDEX {name} IF EXISTS"
        st_print(f"Dropping index: {name}")
        conn.query(drop_query)

    st_print("Database cleared.")


if __name__ == "__main__":
    build_knowledge_graph()