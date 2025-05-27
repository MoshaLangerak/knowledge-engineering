from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def run_query(conn: Neo4jConnection):
    business_name_pub = conn.query("MATCH (b:Business) WHERE b.type = 'pub' RETURN b.name")
    if business_name_pub:
        print("Keys: ", business_name_pub[2])
        print("Summary: ", business_name_pub[1].counters)
        print(f"Pub names: {[record['b.name'] for record in business_name_pub[0][:3]]}")
    else:
        print("No pubs found.")