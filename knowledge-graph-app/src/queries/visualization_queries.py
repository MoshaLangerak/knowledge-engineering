# Modular query logic for visualization: get boroughs, populations, business counts, and ratios

def get_bubble_chart_data(conn, borough_name, year, business_type):
    """
    Returns a dict with boroughs, populations, business counts, and business/population ratios
    for the selected borough and its neighbours, for a given year and business type.
    """
    from .queries import (
        get_borough_and_neighbours,
        get_population_for_boroughs,
        get_business_count_for_boroughs,
    )
    boroughs = get_borough_and_neighbours(conn, borough_name)
    populations = get_population_for_boroughs(conn, boroughs, year)
    business_counts = get_business_count_for_boroughs(conn, boroughs, business_type)
    data = []
    for b in boroughs:
        pop = populations.get(b, 0)
        bus = business_counts.get(b, 0)
        ratio = (bus / pop * 10000) if pop else 0  # per 10,000 people
        data.append({
            "borough": b,
            "population": pop,
            "business_count": bus,
            "business_to_population_ratio": ratio,
        })
    return data


def query_people_business_ratio(conn, business_type):
    query = f"""
    MATCH (b:Borough)<-[:LOCATED_IN]-(bus:Business)-[:OF_TYPE]->(:BusinessType {{name: '{business_type}'}}),
          (b)-[:HAS_POPULATION]->(p:Population)
    RETURN b.name AS borough, 
           COUNT(DISTINCT bus) AS business_count,
           SUM(p.population) AS population
    """
    records, _, keys = conn.query(query)
    return pd.DataFrame([r.data() for r in records])
