import plotly.express as px
import pandas as pd
import streamlit as st

def plot_generic_barchart(
    data,
    x_col="year",
    y_col="population",
    color_col="borough",
    title="Bar Chart",
    color_scheme="Set1",
    x_axis_label=None,
    y_axis_label=None,
    barmode="group"
):
    """
    Plots a generic bar chart from a pandas DataFrame or list of dicts.

    Parameters:
        data: pandas DataFrame or list of dicts
        x_col: Column for x-axis
        y_col: Column for y-axis
        color_col: Column for color grouping
        title: Chart title
        color_scheme: Plotly color sequence name (e.g., 'Set1', 'Viridis')
        x_axis_label: Label for the x-axis (optional)
        y_axis_label: Label for the y-axis (optional)
        barmode: 'group' or 'stack'

    Returns:
        Plotly Figure object or None if no data
    """
    if data is None or len(data) == 0:
        return None

    # Set default axis labels if not provided
    x_axis_label = x_axis_label or x_col.capitalize()
    y_axis_label = y_axis_label or y_col.capitalize()

    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode=barmode,
        color_discrete_sequence=px.colors.qualitative.__dict__.get(color_scheme, px.colors.qualitative.Set1),
        labels={x_col: x_axis_label, y_col: y_axis_label, color_col: color_col.capitalize()},
        title=title,
        orientation='h'  # Ensure horizontal bars
    )
    # Make bars equally spaced and of equal width
    fig.update_layout(
        xaxis=dict(dtick=10),  # for growth rate, adjust as needed
        yaxis=dict(dtick=1, automargin=True, categoryorder='total ascending'),
        bargap=0.2,  # space between bars
        bargroupgap=0.1  # space between groups
    )
    fig.update_traces(marker_line_width=1.5, marker_line_color='black')
    return fig

def plot_distribution_barchart(
    values,
    item_value=None,
    n_bins=10,
    precision=0,  # Added precision as a parameter for clarity
    x_label="Value",
    y_label="Count",
    title="Distribution",
    highlight_color="crimson",
    bar_color="steelblue"
):
    """
    Plots a vertical bar chart of the distribution of values.
    Highlights the bin containing item_value if provided. This version is corrected
    to work with any precision setting.
    """
    values = pd.Series(values).dropna()

    # Create bins with the specified precision
    bins = pd.cut(values, bins=n_bins, precision=precision)
    bin_counts = bins.value_counts().sort_index()

    if precision == 0:
        # Convert intervals to strings and remove '.0' to show as integers
        bin_labels = [str(iv).replace('.0', '') for iv in bin_counts.index]
    else:
        # For other precisions, use the default string representation
        bin_labels = bin_counts.index.astype(str)

    highlight_index = None
    if item_value is not None:
        # Find which bin interval contains the item_value
        for i, interval in enumerate(bin_counts.index):
            if item_value in interval:
                highlight_index = i
                break

    # Create the list of colors based on the found index
    colors = [bar_color] * len(bin_counts)
    if highlight_index is not None:
        colors[highlight_index] = highlight_color
    
    fig = px.bar(
        x=bin_labels,
        y=bin_counts.values,
        labels={"x": x_label, "y": y_label},
        title=title
    )
    # Use the new color list to set the marker colors
    fig.update_traces(marker_color=colors)
    fig.update_layout(xaxis_tickangle=-45, bargap=0.05)
    return fig