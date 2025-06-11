import plotly.graph_objects as go
import networkx as nx
from typing import List, Dict, Any

import plotly.express as px
import pandas as pd


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
    
    # Improve spacing to avoid overlaps
    k_val = 1 / (len(G.nodes) ** 0.05)  # dynamic spacing based on node count
    pos = nx.spring_layout(G, seed=42, k=k_val)

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

    # Get min/max ratio for color normalization
    ratios = [G.nodes[n]['ratio'] for n in G.nodes]
    ratio_min, ratio_max = min(ratios), max(ratios)

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
        sizes.append(max(2, population / 2_500))
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
            colorscale='Viridis',
            color=colors,
            cmin=ratio_min,
            cmax=ratio_max,
            size=sizes,
            opacity=1,
            colorbar=dict(
                thickness=15,
                title='Business/Population Ratio',
                xanchor='left'
            ),
            line_width=2
        )
    )

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

def plot_borough_scatter(data: List[Dict[str, Any]], selected_borough: str) -> go.Figure:
    """
    Generates a scatter plot of boroughs with population on the x-axis and
    business-to-people ratio on the y-axis. The selected borough is highlighted.

    Args:
        data: A list of dictionaries, where each dictionary represents a borough
              and contains 'borough', 'population', and 'business_to_population_ratio'.
        selected_borough: The name of the borough to highlight in the plot.

    Returns:
        A Plotly Figure object representing the scatter plot.
    """
    if not data:
        # Return an empty figure if there's no data
        return go.Figure(layout=go.Layout(title="No data to display"))

    # Convert the list of dictionaries to a pandas DataFrame for easier manipulation
    df = pd.DataFrame(data)

    # Separate the data for the selected borough from the rest
    other_boroughs_df = df[df['borough'] != selected_borough]
    selected_borough_df = df[df['borough'] == selected_borough]

    # Create the figure object
    fig = go.Figure()

    # Add a trace for all other boroughs
    # These will appear as standard blue circles
    fig.add_trace(go.Scatter(
        x=other_boroughs_df['population'],
        y=other_boroughs_df['business_to_population_ratio'],
        mode='markers',
        marker=dict(
            color='rgba(52, 152, 219, 0.7)',  # A nice blue with some transparency
            size=12,
            line=dict(
                color='rgba(41, 128, 185, 1.0)',
                width=1
            )
        ),
        text=other_boroughs_df['borough'],
        hoverinfo='text+x+y',
        name='Other Boroughs'
    ))

    # Add a separate, highlighted trace for the selected borough
    # This will be a larger, more prominent red circle
    if not selected_borough_df.empty:
        fig.add_trace(go.Scatter(
            x=selected_borough_df['population'],
            y=selected_borough_df['business_to_population_ratio'],
            mode='markers',
            marker=dict(
                color='rgba(231, 76, 60, 0.9)',  # A strong red
                size=18,
                symbol='circle',
                line=dict(
                    color='rgba(192, 57, 43, 1.0)',
                    width=2
                )
            ),
            text=selected_borough_df['borough'],
            hoverinfo='text+x+y',
            name=selected_borough
        ))

    # --- Visual Cues for Plot Quadrants ---
    # Calculate boundaries and midpoints for shading and annotations
    x_max = df['population'].max() * 1.05
    y_max = df['business_to_population_ratio'].max() * 1.05
    x_min = df['population'].min() * 0.95
    y_min = df['business_to_population_ratio'].min() * 0.95
    x_mean = df['population'].mean()
    y_mean = df['business_to_population_ratio'].mean()

    # Update the layout of the plot for a cleaner look and more information
    fig.update_layout(
        # title=dict(
        #     text=f'<b>Population vs. Business Ratio in London Boroughs</b><br><i>Highlighting: {selected_borough}</i>',
        #     x=0.5,
        #     font=dict(size=20)
        # ),
        xaxis_title="Population",
        yaxis_title="People to Business Ratio",
        legend_title="Boroughs",
        hovermode='closest',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(gridcolor='rgba(236, 240, 241, 1)'),
        yaxis=dict(gridcolor='rgba(236, 240, 241, 1)'),
        # Add shapes to shade the quadrants
        shapes=[
            # "High Potential" quadrant (top-right)
            go.layout.Shape(
                type="rect", xref="x", yref="y",
                x0=x_mean, y0=y_mean, x1=x_max, y1=y_max,
                fillcolor="rgba(85, 185, 145, 0.15)",
                line=dict(width=0), layer="below"
            ),
            # "Lower Potential" quadrant (bottom-left)
            go.layout.Shape(
                type="rect", xref="x", yref="y",
                x0=x_min, y0=y_min, x1=x_mean, y1=y_mean,
                fillcolor="rgba(230, 126, 126, 0.15)",
                line=dict(width=0), layer="below"
            ),
            # "High Ratio" quadrant (top-left)
            go.layout.Shape(
                type="rect", xref="x", yref="y",
                x0=x_min, y0=y_mean, x1=x_mean, y1=y_max,
                fillcolor="rgba(243, 156, 18, 0.15)",
                line=dict(width=0), layer="below"
            ),
            # "High Population" quadrant (bottom-right)
            go.layout.Shape(
                type="rect", xref="x", yref="y",
                x0=x_mean, y0=y_min, x1=x_max, y1=y_mean,
                fillcolor="rgba(243, 156, 18, 0.15)",
                line=dict(width=0), layer="below"
            )
        ],
        # Add annotations to label the quadrants
        annotations=[
            go.layout.Annotation(
                x=x_max, y=y_max, xref="x", yref="y",
                text="<b>High Potential</b><br>(High Population & Ratio)",
                showarrow=False, xanchor='right', yanchor='top',
                font=dict(color="rgba(39, 174, 96, 1.0)", size=12), align="right"
            ),
            go.layout.Annotation(
                x=x_min, y=y_min, xref="x", yref="y",
                text="<b>Lower Potential</b><br>(Low Population & Ratio)",
                showarrow=False, xanchor='left', yanchor='bottom',
                font=dict(color="rgba(192, 57, 43, 1.0)", size=12), align="left"
            ),
            go.layout.Annotation(
                x=x_min, y=y_max, xref="x", yref="y",
                text="<b><b>Medium Potential</b><br>(Low Population & High Ratio)</b>",
                showarrow=False, xanchor='left', yanchor='top',
                font=dict(color="rgba(211, 84, 0, 1.0)", size=12), align="left"
            ),
            go.layout.Annotation(
                x=x_max, y=y_min, xref="x", yref="y",
                text="<b><b>Medium Potential</b><br>(High Population & Low Ratio)</b>",
                showarrow=False, xanchor='right', yanchor='bottom',
                font=dict(color="rgba(211, 84, 0, 1.0)", size=12), align="right"
            )
        ]
    )

    return fig


def plot_borough_bubble_chart(data):
    df = pd.DataFrame(data)
    fig = px.scatter(
        df,
        x="borough",
        y=[0]*len(df),  # All on one line, or use another dimension if available
        size="population",
        color="business_to_population_ratio",
        color_continuous_scale="Viridis",
        hover_name="borough",
        size_max=60,
        labels={"business_to_population_ratio": "Businesses per 10k"}
    )
    fig.update_yaxes(visible=False)
    fig.update_layout(
        title="Boroughs: Size = Population, Color = Businesses per 10k",
        showlegend=False
    )
    return fig
