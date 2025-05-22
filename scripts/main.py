from scripts.connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from scripts.schema_setup import create_constraints_and_indexes
from scripts.data_importer import import_business_data


def clear_database(conn: Neo4jConnection):
    print("Clearing the database (detaching and deleting all nodes and relationships)...")
    # Detach and delete all nodes (and their relationships)
    query_delete_all = "MATCH (n) DETACH DELETE n"
    conn.query(query_delete_all)
    # Optionally, you might want to drop constraints and indexes if you are truly starting fresh
    # For now, schema_setup is idempotent, so it can run on an empty or existing schema.
    print("Database cleared.")

def build_knowledge_graph():
    print("Starting knowledge graph build process...")
    conn = None
    try:
        conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

        if not conn._Neo4jConnection__driver: # Accessing the private attribute for check
            print("Failed to connect to Neo4j. Aborting build.")
            return

        # CAREFULL: Clear database for a completely fresh build, comment out if not needed
        clear_database(conn)

        create_constraints_and_indexes(conn)

        # 2. Import data
        import_business_data(conn)  

        # 3. Create relationships between imported data
        # create_relationships(conn)

        print("Knowledge graph build process completed successfully!")

    except Exception as e:
        print(f"An error occurred during the build process: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    build_knowledge_graph()