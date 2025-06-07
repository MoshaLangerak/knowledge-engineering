# Get the selected borough and its neighbours
def get_borough_and_neighbours(conn, borough_name):
    query = """
    MATCH (b:Borough {name: $borough_name})
    OPTIONAL MATCH (b)-[:NEIGHBOURS]-(n:Borough)
    RETURN collect(DISTINCT b.name) + collect(DISTINCT n.name) AS borough_names
    """
    result = conn.query(query, parameters={"borough_name": borough_name})
    return result[0][0]["borough_names"] if result and result[0] else []


# Get population for each borough in a given year
def get_population_for_boroughs(conn, borough_names, year):
    query = """
    UNWIND $borough_names AS name
    MATCH (b:Borough {name: name})-[:HAS_POPULATION {year: $year}]->(p:Population)
    RETURN b.name AS borough, p.population AS population
    """
    result = conn.query(query, parameters={"borough_names": borough_names, "year": year})
    return {row["borough"]: row["population"] for row in result[0]} if result and result[0] else {}


# Get number of businesses of a type in each borough
def get_business_count_for_boroughs(conn, borough_names, business_type):
    query = """
    UNWIND $borough_names AS name
    MATCH (b:Borough {name: name})<-[:LOCATED_IN]-(bus:Business)-[:OF_TYPE]->(bt:BusinessType {type: $business_type})
    RETURN b.name AS borough, count(bus) AS business_count
    """
    result = conn.query(query, parameters={"borough_names": borough_names, "business_type": business_type})
    return {row["borough"]: row["business_count"] for row in result[0]} if result and result[0] else {}

# Get all business types 
def get_business_types(conn):
    query = "MATCH (bt:BusinessType) RETURN bt.type AS type ORDER BY type"
    records, _, _ = conn.query(query)
    return [r["type"] for r in records]

# Get all years
def get_years(conn):
    query = "MATCH (p:Population) RETURN DISTINCT p.year AS year ORDER BY year"
    records, _, _ = conn.query(query)
    return [r["year"] for r in records]