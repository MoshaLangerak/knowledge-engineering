import folium
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

    gdf["people_per_business"] = (gdf["population"]/ gdf["business_count"]).round(3)
    return gdf


# Computes the geovisualization (e.g. the polygons for boroughs)
def plot_interactive_map(gdf, business_type, year):
    gdf = gdf.to_crs(4326)                    
    gdf = gdf.dropna(subset=["people_per_business"])
    m = folium.Map(location=[51.509865, -0.118092], zoom_start=10)

    choropleth = folium.Choropleth(
        geo_data=gdf.to_json(),
        name="choropleth",
        data=gdf,
        columns=["borough", "people_per_business"],
        key_on="feature.properties.borough",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"Number of people per {business_type} business in ({year})",
        highlight=True,
        highlight_function=lambda feature: {'color':'transparent'}
    ).add_to(m)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=["borough", "people_per_business"],
            aliases=["Borough:", f"People per {business_type.title()} business:"],
            localize=True,
            labels=True,
            sticky=False,
            style=(
                "background-color: white; "
                "border: 1px solid black; "
                "border-radius: 3px; "
                "padding: 5px;"
            ),
        )
    )

    # Add always-visible borough name labels at centroid
    for _, row in gdf.iterrows():
        folium.map.Marker(
            [row.geometry.centroid.y, row.geometry.centroid.x],
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 10pt; color: black; text-align: center;">{row['borough']}</div>"""
            ),
            tooltip=row['borough']
        ).add_to(m)
    return m
