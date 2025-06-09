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
    quantile_binning=False,
    x_label="Value",
    y_label="Count",
    title="Distribution",
    highlight_color="crimson",
    bar_color="steelblue"
):
    """
    Plots a vertical bar chart of the distribution of values, with optional quantile binning.
    Highlights the bin containing item_value if provided.
    For quantile binning, x labels are quantile numbers (e.g., Q1, Q2, ...).
    """
    values = pd.Series(values).dropna()
    if quantile_binning:
        quantile_labels = [f"{int(100*i/n_bins)}-{int(100*(i+1)/n_bins)}%" for i in range(n_bins)]
        try:
            bins = pd.qcut(values, q=n_bins, labels=quantile_labels, duplicates='drop')
        except ValueError as e:
            st.warning(
                "Could not create the requested number of quantile bins. "
                "Try reducing the number of bins or check your data for duplicate values."
            )
            return px.bar()
        bin_counts = bins.value_counts().sort_index()
        bin_labels = bin_counts.index.tolist()
    else:
        bins = pd.cut(values, bins=n_bins)
        bin_counts = bins.value_counts().sort_index()
        bin_labels = bin_counts.index.astype(str)

    highlight_bin = None
    if item_value is not None:
        extended_values = pd.concat([values, pd.Series([item_value])], ignore_index=True)
        if quantile_binning:
            item_bin = pd.qcut(extended_values, q=n_bins, labels=quantile_labels, duplicates='drop').iloc[-1]
        else:
            item_bin = pd.cut(extended_values, bins=n_bins).iloc[-1]
        highlight_bin = str(item_bin)

    colors = [highlight_color if str(lbl) == highlight_bin else bar_color for lbl in bin_labels]

    fig = px.bar(
        x=bin_labels,
        y=bin_counts.values,
        labels={"x": x_label, "y": y_label},
        title=title
    )
    fig.update_traces(marker_color=colors)
    fig.update_layout(xaxis_tickangle=-45, bargap=0.05)
    return fig
