from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def create_constraints_and_indexes(conn: Neo4jConnection):
    """
    Defines and creates constraints and indexes for the knowledge graph.
    This function should be idempotent (safe to run multiple times).
    """
    print("Setting up constraints and indexes...")

    # Ensures that 'businessId' is unique for all nodes with the label 'Business'
    business_id_constraint = "CREATE CONSTRAINT business_unique_id IF NOT EXISTS FOR (b:Business) REQUIRE b.businessId IS UNIQUE"
    business_type_constraint = "CREATE CONSTRAINT business_type IF NOT EXISTS FOR (b:Business) REQUIRE b.type IS NOT NULL"

    queries = [
        business_id_constraint,
        business_type_constraint,
    ]

    for query in queries:
        print(f"Executing: {query}")
        conn.query(query)

    print("Constraints and indexes setup complete.")

if __name__ == "__main__":
    db_connection = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    if db_connection._Neo4jConnection__driver: # Check if connection was successful
        create_constraints_and_indexes(db_connection)
        db_connection.close()