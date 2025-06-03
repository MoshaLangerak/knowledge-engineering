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


def connect_neighbouring_boroughs(conn: Neo4jConnection, test_boroughs=[], st_print=print):
    """
    Creates symmetric NEIGHBOURS relationships between Borough nodes.
    If test_boroughs is provided, only creates relationships where both boroughs are in test_boroughs.
    """
    st_print("Creating neighbouring borough relationships...")
    df = pd.read_csv("data/processed/neighbouring_boroughs.csv")
    if test_boroughs:
        df = df[df["borough1"].isin(test_boroughs) & df["borough2"].isin(test_boroughs)]
    data = df.to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    MATCH (b1:Borough {name: row.borough1})
    MATCH (b2:Borough {name: row.borough2})
    MERGE (b1)-[:NEIGHBOURS]->(b2)
    MERGE (b2)-[:NEIGHBOURS]->(b1)
    """
    conn.query(query, parameters={"rows": data})
    st_print("Neighbouring borough relationships created.")


def connect_boroughs_to_aggregate(conn: Neo4jConnection, test_boroughs=[], st_print=print):
    """
    Creates PART_OF relationships from Boroughs to aggregate boroughs:
    - Inner / Outer London -> Greater London
    - Boroughs -> Inner London or Outer London (from CSV)
    If test_boroughs is provided, only creates relationships for those boroughs.
    """
    st_print("Creating relationships between boroughs and aggregate boroughs...")

    # Only Inner London and Outer London to Greater London
    query_greater = """
    UNWIND $names AS name
    MATCH (b:Borough {name: name})
    MATCH (g:Borough {name: 'Greater London'})
    MERGE (b)-[:PART_OF]->(g)
    """
    conn.query(query_greater, parameters={"names": ["Inner London", "Outer London"]})

    # Boroughs to Inner/Outer London from CSV
    df = pd.read_csv("data/processed/boroughs_containment.csv")
    if test_boroughs:
        df = df[df["borough"].isin(test_boroughs)]
    data = df.to_dict(orient="records")

    query_agg = """
    UNWIND $rows AS row
    MATCH (b:Borough {name: row.borough})
    MATCH (a:Borough {name: row.aggregate})
    MERGE (b)-[:PART_OF]->(a)
    """
    conn.query(query_agg, parameters={"rows": data})

    st_print("Borough-aggregate relationships created.")
