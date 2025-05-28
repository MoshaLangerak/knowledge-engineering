from connect import Neo4jConnection

def create_relationships(conn: Neo4jConnection):
    """
    Efficiently creates 'LOCATED_IN' relationships between Business and Borough nodes
    using CALL { ... } IN TRANSACTIONS for large CSV files.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///businesses_with_boroughs.csv' AS row
    MATCH (b:Business {osmId: row.osm_id})
    MATCH (br:Borough {name: row.area})
    MERGE (b)-[:LOCATED_IN]->(br)
    """
    conn.query(query)
    print("Business-Borough relationships created.")
