#  Get all boroughs in the graph
def get_all_boroughs(conn):
    """
    Returns a list of all borough names in the dataset, sorted alphabetically.
    """
    query = "MATCH (b:Borough) RETURN b.name AS name ORDER BY name"
    records, _, _ = conn.query(query)
    return [r["name"] for r in records]

# Get all business types in the graph
def get_all_business_types(conn):
    """
    Returns a list of all business types in the dataset, sorted alphabetically.
    """
    query = "MATCH (bt:BusinessType) RETURN bt.type AS type ORDER BY type"
    records, _, _ = conn.query(query)
    return [r["type"] for r in records]

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

# Get number of businesses of a type in each borough (all boroughs)
def get_business_count_for_all_boroughs(conn, business_type):
    """
    Returns a dict {borough: business_count} for all boroughs for the given business type.
    """
    query = """
    MATCH (b:Borough)
    OPTIONAL MATCH (b)<-[:LOCATED_IN]-(bus:Business)-[:OF_TYPE]->(bt:BusinessType {type: $business_type})
    RETURN b.name AS borough, count(bus) AS business_count
    ORDER BY borough
    """
    result = conn.query(query, parameters={"business_type": business_type})
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

# Get population data for a list of boroughs over a range of years
def get_population_for_boroughs_in_range(conn, borough_names, min_year=1999, max_year=2050):
    """
    Fetches all population data for a list of boroughs over a selected year range.
    Returns a list of dicts: [{'borough': ..., 'year': ..., 'population': ...}, ...]
    """
    query = """
    UNWIND $borough_names AS name
    MATCH (b:Borough {name: name})-[:HAS_POPULATION]->(p:Population)
    WHERE p.year >= $min_year AND p.year <= $max_year
    RETURN b.name AS borough, p.year AS year, p.population AS population
    ORDER BY borough, year
    """
    result = conn.query(
        query,
        parameters={
            "borough_names": borough_names,
            "min_year": min_year,
            "max_year": max_year,
        },
    )
    # result[0] is the list of records
    return [row for row in result[0]] if result and result[0] else []

# Get business survival rates for a list of boroughs and years
def get_business_survival_rates_for_boroughs(conn, borough_names, year):
    """
    Fetches business survival rates for a list of boroughs for a single year.
    Returns a list of dicts: [{'borough': ..., 'year': ..., 'one_year_rate': ..., ..., 'five_year_rate': ...}, ...]
    """
    query = """
    UNWIND $borough_names AS name
    MATCH (b:Borough {name: name})-[:HAS_SURVIVAL_RATE]->(s:BusinessSurvival)
    WHERE s.year = $year
    RETURN 
        b.name AS borough, 
        s.year AS year, 
        s.births AS businesses_started,
        s.one_year_rate AS one_year_rate, 
        s.two_year_rate AS two_year_rate, 
        s.three_year_rate AS three_year_rate, 
        s.four_year_rate AS four_year_rate, 
        s.five_year_rate AS five_year_rate
    ORDER BY borough
    """
    result = conn.query(query, parameters={"borough_names": borough_names, "year": year})
    return [row for row in result[0]] if result and result[0] else []

# Get distinct years for business survival rates
def get_survival_years(conn):
    query = "MATCH (s:BusinessSurvival) RETURN DISTINCT s.year AS year ORDER BY year"
    records, _, _ = conn.query(query)
    return [r["year"] for r in records]
