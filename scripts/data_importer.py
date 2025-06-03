from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import pandas as pd

# Why separate BusinessType nodes?
# - Querying: Enables efficient queries for all businesses of a certain type.
# - Normalization: Avoids duplication of type strings across many business nodes.
# - Extensibility: Allows adding attributes to business types in the future.

def import_business_data(conn: Neo4jConnection, test_boroughs=[], st_print=print):
    """
    Imports business data from a CSV using UNWIND.
    If test_boroughs is set, only imports businesses from those boroughs for quick testing.
    """
    st_print("Importing business data...")
    df = pd.read_csv("data/processed/businesses_with_boroughs.csv")
    if test_boroughs:
        df = df[df["area"].isin(test_boroughs)]
    data = df.to_dict(orient="records")
    
    query = """
    UNWIND $rows AS row
    MERGE (bt:BusinessType {type: row.fclass})
    MERGE (b:Business {
        name: row.name_business,
        osmId: row.osm_id
    })
    MERGE (b)-[:OF_TYPE]->(bt)
    """
    conn.query(query, parameters={"rows": data})
    st_print("Business data import complete.")


# Why choose node per borough-year?

# Querying: Easy to get all boroughs for a year, or all years for a borough.
# Updating: Add or update a year’s data without schema changes.
# Extending: Add new attributes (e.g., source, confidence, projections) per year.
# Provenance: Track where each year’s data came from.
def import_population_density_data(conn: Neo4jConnection, test_boroughs=[], st_print=print):
    """
    Imports population density data from a CSV using UNWIND.
    Creates a Population node for each borough-year and links it to the Borough node.
    If test_boroughs is set, only imports population data for those boroughs.
    """
    st_print("Importing population density data...")
    df = pd.read_csv("data/processed/housing_density_borough.csv")
    if test_boroughs:
        df = df[df["Name"].isin(test_boroughs)]
    data = df.to_dict(orient="records")

    query = """
    UNWIND $rows AS row
    MERGE (b:Borough {name: row.Name})
    MERGE (p:Population {
        year: toInteger(row.Year),
        source: row.Source,
        population: toInteger(row.Population),
        population_per_sqkm: toFloat(row.Population_per_square_kilometre)
    })
    MERGE (b)-[:HAS_POPULATION {year: toInteger(row.Year)}]->(p)
    """

    conn.query(query, parameters={"rows": data})
    st_print("Population density data import complete.")


# # old population data import
# def import_population_data(conn: Neo4jConnection):
#     """
#     Imports population data from a CSV using UNWIND.
#     """
#     df = pd.read_csv("data/processed/population_by_borough.csv")
#     data = df.to_dict(orient="records")

#     query = """
#     UNWIND $rows AS row
#     MERGE (b:Borough {
#         name: row.area_name,
#         mid_year_estimate_1939: toInteger(row.mid_year_estimate_1939),
#         mid_year_estimate_1988: toInteger(row.mid_year_estimate_1988),
#         census_2011: toInteger(row.census_2011),
#         projection_2015: toInteger(row.projection_2015),
#         projection_2021: toInteger(row.projection_2021),
#         projection_2031: toInteger(row.projection_2031),
#         projection_2039: toInteger(row.projection_2039)
#     })
#     """
#     conn.query(query, parameters={"rows": data})
#     print("Population data import complete.")


# Example driver code 
# if __name__ == "__main__":
#     db_connection = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
#     if db_connection._Neo4jConnection__driver:
#         import_business_data(db_connection)
#         import_population_data(db_connection)
        