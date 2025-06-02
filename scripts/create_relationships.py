from connect import Neo4jConnection
import pandas as pd

def create_relationships(conn: Neo4jConnection):
    """
    Efficiently creates 'LOCATED_IN' relationships between Business and Borough nodes
    using in-memory data instead of file-based CSV loading.
    """
    df = pd.read_csv("data/processed/businesses_with_boroughs.csv")
    df = df.dropna(subset=['osm_id', 'area'])

    data = df.to_dict(orient="records")[:25]

    query = """
    UNWIND $rows AS row
    MATCH (b:Business {osmId: row.osm_id})
    MATCH (br:Borough {name: row.area})
    MERGE (b)-[:LOCATED_IN]->(br)
    """
    conn.query(query, parameters={"rows": data})
    print("Business-Borough relationships created.")

