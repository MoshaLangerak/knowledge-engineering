
import folium
import pandas as pd
from queries.queries import (
    get_population_for_boroughs, 
    get_business_count_for_boroughs
)

# Computes business per people metric
def compute_ratio_dataframe(conn, gdf, business_type, year):
    gdf = gdf.rename(columns={"NAME": "borough"})

    gdf["population"] = gdf["borough"].map(get_population_for_boroughs(conn, gdf["borough"], year))
    gdf["business_count"] = gdf["borough"].map(get_business_count_for_boroughs(conn, gdf["borough"], business_type))
    gdf["business_count"].replace(0, None, inplace=True)

    gdf["businesses_per_person"] = (gdf["business_count"] / gdf["population"] * 10000).round(3)
    return gdf


# Computes the geovisualization (e.g. the polygons for boroughs)
def plot_interactive_map(gdf, business_type, year):
    gdf = gdf.to_crs(4326)                    
    gdf = gdf.dropna(subset=["businesses_per_person"])
    m = folium.Map(location=[51.509865, -0.118092], zoom_start=10)

    folium.Choropleth(
        geo_data=gdf.to_json(),
        name="choropleth",
        data=gdf,
        columns=["borough", "businesses_per_person"],
        key_on="feature.properties.borough",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"Number of {business_type} businesses per 10k people in ({year})",
        highlight=True,
        highlight_function=lambda feature: {'color':'transparent'}
    ).add_to(m)
    
    
    # choropleth.geojson.add_child(
    #     folium.features.GeoJsonTooltip(
    #         fields=["borough", "businesses_per_person"],
    #         aliases=["Borough:", f"{business_type.title()} businesses per 10k:"],
    #         localize=True,                    
    #         labels=True,                     
    #         sticky=False,                     
    #     )
    # )
    
    for _, row in gdf.iterrows():
        if pd.notna(row.get("businesses_per_person")):
            folium.Popup(f"{row['borough']}: {row['businesses_per_person']:.2f}").add_to(
                folium.Marker(
                    location=[row.geometry.centroid.y, row.geometry.centroid.x],
                    icon=folium.DivIcon(html=f"<div style='font-size: 10pt'>{row['borough']}</div>")
                ).add_to(m)
            )
        
    return m

