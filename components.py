from dash import dcc, html

def selection_layout(projects, position_options, attribute_options, year_options):
    year_min = year_options[0] if year_options else 0
    year_max = year_options[-1] if year_options else 0

    return html.Div([
        html.Div([
            dcc.Dropdown(
                id='project-dropdown',
                options=[{'label': project, 'value': project} for project in projects],
                value=None,
                placeholder="Select Project",
                style={'backgroundColor': 'white', 'color': 'black'}
            )
        ], style={'width': '20%', 'display': 'inline-block'}),
        # Position Dropdown
        html.Div([
            dcc.Dropdown(
                id='position-dropdown',
                options=[{'label': pos, 'value': pos} for pos in position_options],
                multi=True,
                placeholder="Select Positions",
                style={'backgroundColor': 'white', 'color': 'black'}
            )
        ], style={'width': '20%', 'display': 'inline-block','marginLeft': '5%'}),
 
        # Attribute Dropdown
        html.Div([
            dcc.Dropdown(
                id='attribute-dropdown',
                options=[{'label': attr, 'value': attr} for attr in attribute_options],
                multi=True,
                placeholder="Select Attributes",
                style={'backgroundColor': 'white', 'color': 'black'}
            )
        ], style={'width': '20%', 'display': 'inline-block', 'marginLeft': '5%'}),

        # Year Range Slider
        html.Div([
            dcc.RangeSlider(
                id='year-range-slider',
                min=year_min,
                max=year_max,
                value=[year_min, year_max],
                marks={str(year): {'label': str(year), 'style': {'color': 'white', 'fontSize': '14px'}} for year in year_options} if year_options else {},
                step=None,
                className="dark-slider"
            )
        ], style={'width': '20%', 'display': 'inline-block', 'marginLeft': '5%'})
    ], style={'backgroundColor': '#444444', 'padding': '20px', 'color': 'white'})


def graphs_layout():
    return html.Div(id='graphs-container', style={'padding': '20px'})
