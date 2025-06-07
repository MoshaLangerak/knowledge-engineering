import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd


# Why separate BusinessType nodes?
# - Querying: Enables efficient queries for all businesses of a certain type.
# - Normalization: Avoids duplication of type strings across many business nodes.
# - Extensibility: Allows adding attributes to business types in the future.
def import_business_data(conn, test_boroughs=[]):
    """
    Efficiently imports business data and business types.
    """
    st.info("Importing business data...")
    df = pd.read_csv("data/processed/businesses_with_boroughs.csv")
    if test_boroughs:
        df = df[df["area"].isin(test_boroughs)]
    data = df.to_dict(orient="records")

    # Step 1: Create unique BusinessType nodes
    unique_types = [{"type": t} for t in df["fclass"].dropna().unique()]
    type_query = """
    UNWIND $rows AS row
    MERGE (:BusinessType {type: row.type})
    """
    conn.query(type_query, parameters={"rows": unique_types})

    # Step 2: Create businesses and relationships
    business_query = """
    UNWIND $rows AS row
    MATCH (bt:BusinessType {type: row.fclass})
    MERGE (b:Business {
        name: row.name_business,
        osmId: row.osm_id
    })
    MERGE (b)-[:OF_TYPE]->(bt)
    MERGE (bt)-[:TYPE_FOR]->(b)
    """
    conn.query(business_query, parameters={"rows": data})
    st.info("Business data import complete.")


# Why choose node per borough-year?
# - Querying: Easy to get all boroughs for a year, or all years for a borough.
# - Updating: Add or update a year’s data without schema changes.
# - Extending: Add new attributes (e.g., source, confidence, projections) per year.
# - Provenance: Track where each year’s data came from.
def import_population_density_data(conn, test_boroughs=[]):
    """
    Imports population density data from a CSV using UNWIND.
    Creates a Population node for each borough-year and links it to the Borough node.
    If test_boroughs is set, only imports population data for those boroughs.
    """
    st.info("Importing population density data...")
    df = pd.read_csv("data/processed/housing_density_borough.csv")
    if test_boroughs:
        df = df[df["Name"].isin(test_boroughs)]
    data = df.to_dict(orient="records")

    # Step 1: Create unique Borough nodes
    unique_boroughs = [{"name": n} for n in df["Name"].dropna().unique()]
    borough_query = """
    UNWIND $rows AS row
    MERGE (:Borough {name: row.name})
    """
    conn.query(borough_query, parameters={"rows": unique_boroughs})

    # Step 2: Create Population nodes and relationships
    query = """
    UNWIND $rows AS row
    MATCH (b:Borough {name: row.Name})
    MERGE (p:Population {
        year: toInteger(row.Year),
        source: row.Source,
        population: toInteger(row.Population),
        population_per_sqkm: toFloat(row.Population_per_square_kilometre)
    })
    MERGE (b)-[:HAS_POPULATION {year: toInteger(row.Year)}]->(p)
    """
    conn.query(query, parameters={"rows": data})
    st.info("Population density data import complete.")


def import_business_survival_rate_data(conn, test_boroughs=[]):
    """
    Imports business survival rate data from CSV.
    Creates a BusinessSurvival node for each borough-year and links it to the Borough node.
    Only sets properties for non-null values in the dataframe.
    If test_boroughs is set, only imports data for those boroughs.
    """
    st.info("Importing business survival rate data...")
    df = pd.read_csv("data/processed/boroughs_business_survival_rate.csv")
    if test_boroughs:
        df = df[df["area"].isin(test_boroughs)]
    df = df.replace({np.nan: None})

    # Only include non-null properties for each row
    def row_to_props(row):
        props = {
            "year": int(row["year"]),
        }
        if row["births"] is not None:
            props["births"] = int(row["births"])
        for n in range(1, 6):
            col = f"{n}_year_survival_rate"
            if row.get(col) is not None:
                props[f"{n}_year_rate"] = float(row[col])
        return {
            "area": row["area"],
            "props": props
        }

    data = [row_to_props(row) for _, row in df.iterrows()]

    # Create BusinessSurvival nodes and relationships, only setting non-null properties
    query = """
    UNWIND $rows AS row
    MATCH (b:Borough {name: row.area})
    MERGE (bs:BusinessSurvival {year: row.props.year})
    SET bs += row.props
    MERGE (b)-[:HAS_BUSINESS_SURVIVAL {year: row.props.year}]->(bs)
    """
    conn.query(query, parameters={"rows": data})
    st.info("Business survival rate data import complete.")


def import_borough_shapes():
    return gpd.read_file("data/raw/gis-boundaries-london/ESRI/London_Borough_Excluding_MHW.shp")


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
