from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def import_business_data(conn: Neo4jConnection):
    """
    Imports business data from a CSV file into the Neo4j database.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///businesses_with_boroughs.csv' AS row
    CREATE (b:Business {name: row.name_business})
    SET
        b.osmId = row.osm_id,
        b.type = row.fclass
    """
    conn.query(query)
    print("Business data import complete.")

def import_population_data(conn: Neo4jConnection):
    """
    Imports population data from a CSV file into the Neo4j database.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///population_by_borough.csv' AS row
    CREATE (b:Borough {name: row.area_name})
    SET
        b.mid_year_estimate_1939 = toInteger(row.mid_year_estimate_1939),
        b.mid_year_estimate_1988 = toInteger(row.mid_year_estimate_1988),
        b.census_2011 = toInteger(row.census_2011),
        b.projection_2015 = toInteger(row.projection_2015),
        b.projection_2021 = toInteger(row.projection_2021),
        b.projection_2031 = toInteger(row.projection_2031),
        b.projection_2039 = toInteger(row.projection_2039)
    """
    conn.query(query)
    print("Population data import complete.")


if __name__ == "__main__":
    db_connection = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    if db_connection._Neo4jConnection__driver:
        import_business_data(db_connection)
        import_population_data(db_connection)
        