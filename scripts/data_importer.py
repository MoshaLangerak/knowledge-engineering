from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def import_business_data(conn: Neo4jConnection):
    """
    Imports business data from a CSV file into the Neo4j database.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///businesses_with_boroughs.csv' AS row
    CREATE (b:Business {
        osmId: row.osm_id,
        name: row.name_business,
        type: row.fclass,
    })
    """
    conn.query(query)
    print("Data import complete.")

if __name__ == "__main__":
    db_connection = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    if db_connection._Neo4jConnection__driver:
        import_business_data(db_connection)
        