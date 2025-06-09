import plotly.express as px

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
