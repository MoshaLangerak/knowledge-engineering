
import folium
import pandas as pd
from queries.queries import (
    get_population_for_boroughs, 
    get_business_count_for_boroughs
)

# Computes people per business ratio dataframe
def compute_ratio_dataframe(conn, gdf, business_type, year):
    borough_names = gdf["NAME"].tolist()
    population_dict = get_population_for_boroughs(conn, borough_names, year)
    business_count_dict = get_business_count_for_boroughs(conn, borough_names, business_type)

    gdf = gdf.rename(columns={"NAME": "borough"})
    gdf["population"] = gdf["borough"].map(population_dict)
    gdf["business_count"] = gdf["borough"].map(business_count_dict)
    gdf["people_per_business"] = gdf["population"] / gdf["business_count"]
    return gdf


def plot_interactive_map(gdf, business_type, year):
    gdf = gdf.to_crs(epsg=4326)
    m = folium.Map(location=[51.509865, -0.118092], zoom_start=10)
    folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        data=gdf,
        columns=["borough", "people_per_business"],
        key_on="feature.properties.borough",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"People per {business_type} ({year})"
    ).add_to(m)
    
    for _, row in gdf.iterrows():
        if pd.notna(row.get("people_per_business")):
            folium.Popup(f"{row['borough']}: {row['people_per_business']:.2f}").add_to(
                folium.Marker(
                    location=[row.geometry.centroid.y, row.geometry.centroid.x],
                    icon=folium.DivIcon(html=f"<div style='font-size: 10pt'>{row['borough']}</div>")
                ).add_to(m)
            )
    return m
