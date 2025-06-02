from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import pandas as pd

def import_business_data(conn: Neo4jConnection):
    """
    Imports business data from a CSV using UNWIND.
    """
    df = pd.read_csv("data/processed/businesses_with_boroughs.csv")

    data = df.to_dict(orient="records")
    
    query = """
    UNWIND $rows AS row
    CREATE (b:Business {
        name: row.name_business,
        osmId: row.osm_id,
        type: row.fclass
    })
    """
    conn.query(query, parameters={"rows": data})
    print("Business data import complete.")

def import_population_data(conn: Neo4jConnection):
    """
    Imports population data from a CSV using UNWIND.
    """
    df = pd.read_csv("data/processed/population_by_borough.csv")
    df = df.fillna(0)

    data = df.to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    CREATE (b:Borough {
        name: row.area_name,
        mid_year_estimate_1939: toInteger(row.mid_year_estimate_1939),
        mid_year_estimate_1988: toInteger(row.mid_year_estimate_1988),
        census_2011: toInteger(row.census_2011),
        projection_2015: toInteger(row.projection_2015),
        projection_2021: toInteger(row.projection_2021),
        projection_2031: toInteger(row.projection_2031),
        projection_2039: toInteger(row.projection_2039)
    })
    """
    conn.query(query, parameters={"rows": data})
    print("Population data import complete.")


# Example driver code 
# if __name__ == "__main__":
#     db_connection = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
#     if db_connection._Neo4jConnection__driver:
#         import_business_data(db_connection)
#         import_population_data(db_connection)
        