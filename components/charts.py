import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
import statsmodels.api as sm
import scipy.stats as stats
from scipy.stats import gaussian_kde
import math




def create_funnel_plot(data, y_col, x_col, text_info="value+percent previous", title="Funnel Plot", x_title="Number of Sessions", y_title="Event Type", height=600, width=800, subplots=False, subplot_titles=None, nrows=None, ncols=None, horizontal_spacing=0.1, vertical_spacing=0.1):
    """
    Create a funnel plot with customizable options and an option to create subplots.

    Parameters:
    - data: DataFrame or list of DataFrames containing the data for the funnel plot(s)
    - y_col: Column name for the y-axis
    - x_col: Column name for the x-axis
    - text_info: Information to display on the funnel plot (default: "value+percent previous")
    - title: Title of the funnel plot
    - x_title: Title for the x-axis
    - y_title: Title for the y-axis
    - height: Height of the layout
    - width: Width of the layout
    - subplots: Boolean indicating whether to create subplots
    - subplot_titles: List of titles for the subplots (required if subplots=True)
    - nrows: Number of rows for the subplots (default: 1)
    - ncols: Number of columns for the subplots (default: 1)
    - horizontal_spacing: Horizontal spacing between subplots (default: 0.1)
    - vertical_spacing: Vertical spacing between subplots (default: 0.1)
    """
    if subplots:
        if subplot_titles is None or len(subplot_titles) != nrows * ncols:
            raise ValueError("For subplots, 'subplot_titles' must be provided and match the number of subplots (nrows * ncols).")
        
        fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=subplot_titles, horizontal_spacing=horizontal_spacing, vertical_spacing=vertical_spacing, specs=[[{"type": "funnel"}]*ncols]*nrows)
        
        for i, df in enumerate(data):
            row = (i // ncols) + 1
            col = (i % ncols) + 1
            fig.add_trace(go.Funnel(
                y=df[y_col],
                x=df[x_col],
                textinfo=text_info,
                marker=dict(opacity=0.7)
            ), row=row, col=col)
    else:
        fig = go.Figure()
        fig.add_trace(go.Funnel(
            y=data[y_col],
            x=data[x_col],
            textinfo=text_info,
            marker=dict(opacity=0.7)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        height=height,
        width=width,
        margin=dict(l=50, r=50, t=100, b=50),
        # title_pos=title_pos,
        title_font_size= 24,
        title_y=0.95,
        showlegend=False
    )
    
    # fig.show()

    return fig


def create_bar_chart(df, x_col, y_col, title, x_label, y_label, decimal_places=2, format_type='f', fig_name='bar_chart', height=600):
    """
    Create a bar chart with customizable options.

    Parameters:
    - df: DataFrame containing the data
    - x_col: Column name for the x-axis
    - y_col: Column name for the y-axis
    - title: Title of the chart
    - x_label: Label for the x-axis
    - y_label: Label for the y-axis
    - decimal_places: Number of decimal places for the y values
    - format_type: Format type for the y values ('f' for fixed-point, 's' for scientific notation)
    - fig_name: Name of the figure file (without extension)
    - height: Height of the chart
    """

        # Validate the format_type
    if format_type not in ['f', 's']:
        raise ValueError("format_type must be either 'f' for fixed-point or 's' for scientific notation.")
    # Create the bar chart
    fig = px.bar(df, 
                 x=x_col, 
                 y=y_col, 
                 title=title,
                 labels={y_col: y_label, x_col: x_label},
                 color=x_col)

    # Format the text with the specified number of decimal places
    text_template = f'%{{y:.{decimal_places}{format_type}}}'
    fig.update_traces(texttemplate=text_template, textposition='outside')

    # Update the layout
    fig.update_layout(
        height=height,   # Set the height
        margin=dict(l=20, r=20, t=50, b=20)  # Set the margins
    )

    # Show the figure
    # fig.show()
    return fig


def create_bar_chart(df, x_col, y_col, title, x_label, y_label, decimal_places=2, format_type='f', fig_name='bar_chart', height=600):
    """
    Create a bar chart with customizable options.

    Parameters:
    - df: DataFrame containing the data
    - x_col: Column name for the x-axis
    - y_col: Column name for the y-axis
    - title: Title of the chart
    - x_label: Label for the x-axis
    - y_label: Label for the y-axis
    - decimal_places: Number of decimal places for the y values
    - format_type: Format type for the y values ('f' for fixed-point, 's' for scientific notation)
    - fig_name: Name of the figure file (without extension)
    - height: Height of the chart
    """

    # Validate the format_type
    if format_type not in ['f', 's']:
        raise ValueError("format_type must be either 'f' for fixed-point or 's' for scientific notation.")
    
    # Create the vertical bar chart
    fig = px.bar(df, 
                 x=x_col, 
                 y=y_col, 
                 title=title,
                 labels={y_col: y_label, x_col: x_label},
                 color=x_col,
                 orientation='v')  # Set orientation to vertical

    # Format the text with the specified number of decimal places
    text_template = f'%{{y:.{decimal_places}{format_type}}}'
    fig.update_traces(texttemplate=text_template, textposition='outside')

    # Update the layout
    fig.update_layout(
        height=height,   # Set the height
        margin=dict(l=20, r=20, t=50, b=20)  # Set the margins
    )

    # Show the figure
    # fig.show()
    return fig


def create_line_plot_with_mean(data, x_col, y_col, mean_y, mean_line_color='green', mean_line_width=2, mean_line_dash='dash', mean_line_text='Mean Conversion Rate', mean_line_position='top left', labels=None, title='Line Plot', width=1200, height=600):
    """
    Create a line plot with an optional mean line.

    Parameters:
    - data: DataFrame containing the data for the line plot
    - x_col: Column name for the x-axis
    - y_col: Column name for the y-axis
    - mean_y: Y value for the mean line
    - mean_line_color: Color of the mean line (default: 'green')
    - mean_line_width: Width of the mean line (default: 2)
    - mean_line_dash: Dash style of the mean line (default: 'dash')
    - mean_line_text: Annotation text for the mean line (default: 'Mean Conversion Rate')
    - mean_line_position: Position of the annotation text (default: 'top left')
    - labels: Dictionary for axis labels (default: None)
    - title: Title of the plot (default: 'Line Plot')
    - width: Width of the figure (default: 1200)
    - height: Height of the figure (default: 600)
    """
    fig = px.line(data, 
                  x=x_col, 
                  y=y_col, 
                  labels=labels, 
                  title=title, 
                  width=width, 
                  height=height)
    
    fig.add_hline(y=mean_y, 
                  line=dict(color=mean_line_color, width=mean_line_width, dash=mean_line_dash),
                  annotation_text=mean_line_text, 
                  annotation_position=mean_line_position)
    
    # fig.show()
    return fig


def create_scatter_plot(data, x_col, y_col, color_col, size_col, title='Scatter Plot', labels=None, hover_data=None, x_grid_opacity=0.05, y_grid_opacity=0.05, width=800, height=600):
    """
    Create a scatter plot with customizable options.

    Parameters:
    - data: DataFrame containing the data for the scatter plot
    - x_col: Column name for the x-axis
    - y_col: Column name for the y-axis
    - color_col: Column name for the color dimension
    - size_col: Column name for the size dimension
    - title: Title of the plot (default: 'Scatter Plot')
    - labels: Dictionary for axis labels (default: None)
    - hover_data: List of columns to display in the hover tooltip (default: None)
    - x_grid_opacity: Opacity of the x-axis grid lines (default: 0.05)
    - y_grid_opacity: Opacity of the y-axis grid lines (default: 0.05)
    - width: Width of the figure (default: 800)
    - height: Height of the figure (default: 600)
    """
    fig = px.scatter(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=title,
        labels=labels,
        hover_data=hover_data,
        width=width,
        height=height
    )
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridwidth=0.25, gridcolor=f'rgba(0,0,0,{x_grid_opacity})'),
        yaxis=dict(showgrid=True, gridwidth=0.25, gridcolor=f'rgba(0,0,0,{y_grid_opacity})')
    )
    
    # fig.show()
    return fig
    

def create_hist_plot(df, column, title, x_label, y_label, figsize=(10, 6), nbins=15):
    """
    Create a histogram plot with smooth KDE overlaid using Plotly.

    Parameters:
    - df: DataFrame containing the data
    - column: Column name for the data to be visualized
    - title: Title of the plot
    - x_label: Label for the x-axis
    - y_label: Label for the y-axis
    - figsize: Tuple specifying the figure size (width, height)
    - nbins: Number of bins for the histogram
    """
    
    fig = go.Figure()

    # Create histogram
    hist, bins = np.histogram(df[column], bins=nbins, density=True)

    # Add histogram bars
    fig.add_trace(go.Bar(x=bins[:-1], y=hist, marker=dict(color='rgba(17, 37, 154, 0.8)', line=dict(color='black', width=1)), name='Histogram'))

    # Calculate KDE
    kde = gaussian_kde(df[column])
    kde_values = kde(bins[:-1])

    # Add KDE line
    fig.add_trace(go.Scatter(x=bins[:-1], y=kde_values, mode='lines', name='KDE'))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,

    )

    # fig.show()
    return fig