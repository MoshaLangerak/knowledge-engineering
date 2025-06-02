import streamlit as st
import pandas as pd
from connect import Neo4jConnection, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from main import build_knowledge_graph
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile


def show_graph_view(records):

    def safe_label(entity):
        return str(entity.get("name") or entity.get("id") or repr(entity))


    def format_tooltip(entity):
        return "\n".join([f"{k}: {v}" for k, v in entity.items()])

    def get_node_color(entity):
        if entity.get("type"):
            return "#97C2FC"  # Borough color
        else:
            return "#32BF49"

    G = nx.DiGraph()

    for record in records:
        source = record["source"]
        target = record["target"]
        relation = record["relation"]

        source_label = safe_label(source)
        target_label = safe_label(target)

        # Improved tooltip formatting
        source_tooltip = format_tooltip(source)
        target_tooltip = format_tooltip(target)

        G.add_node(source_label, label=source_label, title=source_tooltip, color=get_node_color(source))
        G.add_node(target_label, label=target_label, title=target_tooltip, color=get_node_color(target))
        G.add_edge(source_label, target_label, title=relation, label=relation, arrows="to", font={"size": 14, "color": "white", "face": "arial", "strokeWidth": 0, "bold": False}
)

    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    net.repulsion(node_distance=120, spring_length=200)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp_file:
        net.save_graph(tmp_file.name)

        # Read, patch styles, and embed
        with open(tmp_file.name, 'r', encoding='utf-8') as f:
            html = f.read()

        # … after saving `net.save_graph(tmp_file.name)` and reading it into `html` …
        style_patch = """
        <style>
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #222222 !important;
            height: 100%;
            width: 100%;
        }

        #mynetwork,
        #mynetwork > div {
            width: 100% !important;
            height: 600px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            background-color: #222222 !important;
        }

        #mynetwork canvas {
            display: block !important;
            width: 100% !important;
            height: 600px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            outline: none !important;
            background-color: #222222 !important;
        }
        </style>

        <script>
        window.addEventListener("load", () => {
            const container = document.getElementById("mynetwork");
            if (container && container.network) {
            container.network.fit();
            }
        });
        </script>
        """
        patched_html = html.replace("</head>", style_patch + "</head>")

        # Finally embed with exactly 620px total height (600px for the canvas + 20px margin if you want a hair’s‐breadth),
        # and turn off scrolling so no extra white shows up:
        components.html(patched_html, height=620, scrolling=False)



# Initialize Neo4j connection
def get_connection():
    return Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

conn = get_connection()

st.title("London-DB")

if st.sidebar.button("Build Knowledge Graph"):
    try:
        build_knowledge_graph()
        st.success("Knowledge graph build completed successfully!")
    except Exception as e:
        st.error(f"An error occurred during graph build: {e}")

st.sidebar.markdown("---")

# Sidebar: Select or enter Cypher query
preset_queries = {
    "Boroughs": "MATCH (b:Borough) RETURN b LIMIT 25",
    "Businesses": "MATCH (b:Business) RETURN b LIMIT 25",
    "Relationships": "MATCH (a)-[r]->(b)  RETURN a AS source, type(r) AS relation, b AS target  LIMIT 25"
}
selection = st.sidebar.selectbox("Choose a table", list(preset_queries.keys()))

# Run query
if st.sidebar.button("Show"):
    query = preset_queries[selection]
    records, summary, keys = conn.query(query)

    if records:
        data = [record.data() for record in records]
        flattened_data = []
        first_row = data[0] if data else {}

        if "source" in first_row and "target" in first_row and "relation" in first_row:
            # Handle relationship result
            for row in data:
                flat_row = {
                    "source": row["source"].get("name"),
                    "relation": row.get("relation"),
                    "target": row["target"].get("name")
                }
                flattened_data.append(flat_row)
        else:
            # Handle entity result
            for row in data:
                for key, entity in row.items():
                    flattened_data.append(entity)
                        
        df = pd.DataFrame(flattened_data)
        df = df.fillna("N/A")
        st.dataframe(df)          
        
    else:
        st.warning("No results or query failed.")

st.sidebar.markdown("---")

st.sidebar.markdown("### Choose visualization mode")
col1, col2 = st.sidebar.columns([1, 1])  # Equal but tight
with col1:
    graph_btn = st.button("Graph", use_container_width=True)
with col2:
    map_btn = st.button("Geography", use_container_width=True)


if graph_btn:
    # Run a relationship query to fetch the graph data
    graph_query = "MATCH (a)-[r]->(b) RETURN a AS source, type(r) AS relation, b AS target LIMIT 100"
    records, _, _ = conn.query(graph_query)

    if records:
        show_graph_view(records)
    else:
        st.warning("No relationships found to visualize.")


if map_btn:
    st.subheader("Geography View")
    st.info("Map visualization will appear here")

# Examples of relationship and entity records returned by neo4j
# {'source': {'osmId': 25496840, 'name': '26 Furnival Street', 'type': 'pub'}, 'relation': 'LOCATED_IN', 'target': {'mid_year_estimate_1988': 6200, 'projection_2031': 10843, 'projection_2021': 9559, 'name': 'City of London', 'mid_year_estimate_1939': 9000, 'projection_2015': 8101, 'census_2011': 7375, 'projection_2039': 11623}}
# {'b': {'mid_year_estimate_1988': 6200, 'projection_2031': 10843, 'projection_2021': 9559, 'name': 'City of London', 'mid_year_estimate_1939': 9000, 'projection_2015': 8101, 'census_2011': 7375, 'projection_2039': 11623}}