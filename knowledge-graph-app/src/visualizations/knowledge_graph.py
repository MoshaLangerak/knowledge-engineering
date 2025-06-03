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
        G.add_edge(source_label, target_label, title=relation, label=relation, arrows="to", font={"size": 14, "color": "white", "face": "arial", "strokeWidth": 0, "bold": False})

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
        