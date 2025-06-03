import plotly.graph_objects as go
import networkx as nx
from typing import List, Dict, Any

def plot_borough_business_graph(data: List[Dict[str, Any]], selected_borough: str) -> go.Figure:
    """
    Plots a network graph of boroughs and their connections to the selected borough.

    Node size: Proportional to population
    Node color: Business-to-population ratio per 10,000 people
    """
    # Build graph
    G = nx.Graph()
    
    # Add nodes with attributes
    for d in data:
        G.add_node(d['borough'], 
                   population=d['population'], 
                   ratio=d['business_to_population_ratio'])

    # Add edges from selected borough to others
    for d in data:
        b = d['borough']
        if b != selected_borough:
            G.add_edge(selected_borough, b)
    
    # Layout
    pos = nx.spring_layout(G, seed=42)

    # Edges
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Nodes
    node_x, node_y, sizes, colors, labels, hovers = [], [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        attr = G.nodes[node]
        population = attr['population']
        ratio = attr['ratio']
        business_count = int(population * ratio)

        node_x.append(x)
        node_y.append(y)
        sizes.append(max(10, population / 1000))
        colors.append(ratio)
        labels.append(node)
        hovers.append(
            f"{node}<br>Population: {population:,}<br>Businesses: {business_count:,}<br>Ratio: {ratio:.3f}"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=labels,
        textposition='bottom center',
        hoverinfo='text',
        hovertext=hovers,
        marker=dict(
            showscale=True,
            colorscale='Blues',
            color=colors,
            size=sizes,
            colorbar=dict(
                thickness=15,
                title='Business/Population Ratio',
                xanchor='left'
            ),
            line_width=2
        )
    )

    # Final layout using current Plotly syntax
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text=f'Connections of {selected_borough}',
                font=dict(size=16),
                x=0.5
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[dict(
                text="Node size = population<br>Node color = business/population ratio",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    return fig
