from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def run_query(conn: Neo4jConnection):
    business_name_pub = conn.query("MATCH (b:Business) WHERE b.type = 'pub' RETURN b.name")
    if business_name_pub:
        print("Keys: ", business_name_pub[2])
        print("Summary: ", business_name_pub[1].counters)
        print(f"Pub names: {[record['b.name'] for record in business_name_pub[0][:3]]}")
    else:
        print("No pubs found.")

def example_query_borough_businesses(conn: Neo4jConnection):
    """
    For each Borough, get up to 10 connected Business nodes and their LOCATED_IN relationships.
    """
    query = """
    MATCH (br:Borough)
    CALL {
        WITH br
        MATCH (b:Business)-[r:LOCATED_IN]->(br)
        RETURN b, r
        LIMIT 10
    }
    RETURN br, b, r
    """
    result = conn.query(query)
    if result and result[0]:
        print(f"Example: Borough '{result[0][0]['br']['name']}' has businesses like {[rec['b']['name'] for rec in result[0][:3]]}")
    else:
        print("No borough-business relationships found.")