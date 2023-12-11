import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objs as go
import matplotlib.colors as mc
import colorsys

# Define colors
colors = ['rgba(255, 99, 132, 0.75)', 'rgba(54, 162, 235, 0.75)', 'rgba(255, 99, 132, 0.55)', 'rgba(54, 162, 235, 0.55)']

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

def generate_line_chart(data, attribute, overall_stats=None):
    if overall_stats == 1:
        title = "CA vs PA Mean Over Years"
    elif overall_stats == 2:
        title = "Player Age Distribution Over Years"
    else:
        title = f"{attribute} Mean Over Years"

    fig = go.Figure()

    if overall_stats == 2:
        # Group data by Year and Age and count the number of players
        grouped_data = data.groupby(['Year', 'Age']).size().unstack(fill_value=0)

        # Calculate the cumulative sum for stacked lines
        cumulative = grouped_data.cumsum(axis=1)

        # Add traces for each age group
        for age in cumulative.columns:
            fig.add_trace(go.Scatter(
                x=cumulative.index,
                y=cumulative[age],
                mode='lines',
                name=f'Age {age}',
                stackgroup='one'  # This property stacks the lines
            ))

    elif overall_stats == 1:
        # Mean values
        ca_mean_values = data.groupby('Year')["Current Ability"].mean()
        fig.add_trace(go.Scatter(
            x=ca_mean_values.index,
            y=ca_mean_values.values,
            mode='lines',
            name="Current Ability Mean",
            line=dict(color=colors[0])
        ))

        pa_mean_values = data.groupby('Year')['Potential Ability'].mean()
        fig.add_trace(go.Scatter(
            x=pa_mean_values.index,
            y=pa_mean_values.values,
            mode='lines',
            name='Potential Ability Mean',
            line=dict(color=colors[1])
        ))

        # Median values
        ca_median_values = data.groupby('Year')["Current Ability"].median()
        fig.add_trace(go.Scatter(
            x=ca_median_values.index,
            y=ca_median_values.values,
            mode='lines',
            name="Current Ability Median",
            line=dict(color=colors[2])
        ))

        pa_median_values = data.groupby('Year')['Potential Ability'].median()
        fig.add_trace(go.Scatter(
            x=pa_median_values.index,
            y=pa_median_values.values,
            mode='lines',
            name='Potential Ability Median',
            line=dict(color=colors[3])
        ))

    else:
        mean_values = data.groupby('Year')[attribute].mean()
        fig.add_trace(go.Scatter(
            x=mean_values.index,
            y=mean_values.values,
            mode='lines',
            name=f"{attribute} Mean",
            line=dict(color=colors[1])
        ))
        
        median_values = data.groupby('Year')[attribute].median()
        fig.add_trace(go.Scatter(
            x=median_values.index,
            y=median_values.values,
            mode='lines',
            name=f"{attribute} Median",
            line=dict(color=colors[3])
        ))

        ca_mean_values = data.groupby('Year')["Current Ability"].mean()
        expected_mean = mean_values.iloc[0] * (ca_mean_values / ca_mean_values.iloc[0])
        fig.add_trace(go.Scatter(
            x=expected_mean.index,
            y=expected_mean.values,
            mode='lines',
            name=f'Expected {attribute} (Based on CA Mean)',
            line=dict(color=colors[0])
        ))
        
        
        ca_median_values = data.groupby('Year')["Current Ability"].median()
        expected_mean = mean_values.iloc[0] * (ca_median_values / ca_median_values.iloc[0])
        fig.add_trace(go.Scatter(
            x=expected_mean.index,
            y=expected_mean.values,
            mode='lines',
            name=f'Expected {attribute} (Based on CA Median)',
            line=dict(color=colors[2])
        ))

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
            y=1,  # Adjusted to be within [0, 1]
            x=0.5,
            xanchor='center'
        ),
        margin=dict(b=150)  # Increase bottom margin for title and legend
    )
    fig.update_layout(autosize=True)
