from connect import Neo4jConnection
import pandas as pd

def connect_businesses_to_boroughs(conn: Neo4jConnection, test_boroughs=[], st_print=print):
    """
    Efficiently creates 'LOCATED_IN' relationships between Business and Borough nodes.
    If test=True, only creates relationships for two boroughs.
    """
    st_print("Creating relationships between businesses and boroughs...")
    df = pd.read_csv("data/processed/businesses_with_boroughs.csv")
    if test_boroughs:
        df = df[df["area"].isin(test_boroughs)]
    data = df.to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    MATCH (b:Business {osmId: row.osm_id})
    MATCH (br:Borough {name: row.area})
    MERGE (b)-[:LOCATED_IN]->(br)
    """
    conn.query(query, parameters={"rows": data})
    st_print("Business-Borough relationships created.")
