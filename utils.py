import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objs as go

# Define colors
colors = ['rgba(255, 99, 132, 0.75)', 'rgba(54, 162, 235, 0.75)']

def generate_box_plot(data, attribute, years, title):
    """
    Generate a box plot for a given attribute comparing the first and last year.
    """
    fig = go.Figure(data=[go.Box(y=data[data['Year'] == year][attribute], 
                                 name=str(year), 
                                 marker_color=colors[i]) 
                          for i, year in enumerate(years)])

    update_fig_layout(fig, title)

    return fig

def generate_line_chart(data, attribute, title, ca_column=None):
    """
    Generate a line chart showing the mean of an attribute over all years, with a title.
    If ca_column is provided, it also shows the expected mean based on Current Ability.
    """
    mean_values = data.groupby('Year')[attribute].mean()
    fig = go.Figure(data=go.Scatter(x=mean_values.index, 
                                    y=mean_values.values, 
                                    mode='lines', 
                                    name=attribute,
                                    line=dict(color=colors[1])))

    if ca_column:
        ca_mean_values = data.groupby('Year')[ca_column].mean()
        expected_mean = mean_values.iloc[0] * (ca_mean_values / ca_mean_values.iloc[0])
        fig.add_trace(go.Scatter(x=expected_mean.index, 
                                 y=expected_mean.values, 
                                 mode='lines', 
                                 name=f'Expected {attribute}',
                                 line=dict(color=colors[0])))
    else:
        pa_mean_values = data.groupby('Year')['Potential Ability'].mean()
        fig.add_trace(go.Scatter(x=pa_mean_values.index, 
                                 y=pa_mean_values.values, 
                                 mode='lines', 
                                 name=f'Potential Ability',
                                 line=dict(color=colors[0])))
                                 

    update_fig_layout(fig, title)

    return fig

def generate_combined_histogram_kde(data, attribute, years, title):
    """
    Generate a combined normalized histogram and KDE for the first and last year of a given attribute, with a title.
    """
    fig = go.Figure()

    for i, year in enumerate(years):
        year_data = data[data['Year'] == year][attribute].dropna()
        
        # Histogram
        hist = go.Histogram(x=year_data, 
                                   name=f"Histogram {year}", 
                                   opacity=0.75,
                                   marker_color=colors[i])
        hist = hist.to_plotly_json()
        hist['yaxis'] = 'y2'
        fig.add_trace(go.Histogram(hist))

        # KDE
        kde = gaussian_kde(year_data)
        x_range = np.linspace(year_data.min(), year_data.max(), 500)
        fig.add_trace(go.Scatter(x=x_range, 
                                 y=kde(x_range), 
                                 mode='lines', 
                                 name=f'KDE {year}',
                                 line=dict(color=colors[i])))

    # Update layout to use a secondary y-axis for the histogram
    fig.update_layout(
        barmode='overlay',
        yaxis2=dict(
            overlaying='y',
            side='left',
            visible=False
        )
    )

    update_fig_layout(fig, title)
    return fig

def update_fig_layout(fig, title):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showline=True,
            linewidth=0.5,
            linecolor='darkgrey',
            mirror=False
        ),
        yaxis=dict(
            showline=True,
            linewidth=0.5,
            linecolor='darkgrey',
            mirror=False
        ),
        legend=dict(
            y=-0.3,  # Adjust as needed
            xanchor='center',
            x=0.5,
            orientation='h'
        ),
        title=dict(
            text=title,
            y=0.05,  # Adjusted to be within [0, 1]
            x=0.5,
            xanchor='center'
        ),
        margin=dict(b=150)  # Increase bottom margin for title and legend
    )
    fig.update_layout(autosize=True)
