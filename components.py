from dash import dcc, html

def selection_layout(position_options, attribute_options, year_options):
    return html.Div([
        # Position Dropdown
        html.Div([
            dcc.Dropdown(
                id='position-dropdown',
                options=[{'label': pos, 'value': pos} for pos in position_options],
                multi=True,
                value=position_options[4:6],
                placeholder="Select Positions",
                style={'backgroundColor': 'white', 'color': 'black'}
            )
        ], style={'width': '30%', 'display': 'inline-block'}),

        # Attribute Dropdown
        html.Div([
            dcc.Dropdown(
                id='attribute-dropdown',
                options=[{'label': attr, 'value': attr} for attr in attribute_options],
                multi=True,
                value=attribute_options[15:16],
                placeholder="Select Attributes",
                style={'backgroundColor': 'white', 'color': 'black'}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '5%'}),

        # Year Range Slider
        html.Div([
            dcc.RangeSlider(
                id='year-range-slider',
                min=year_options[0],
                max=year_options[-1],
                value=[year_options[0], year_options[-1]],
                marks={str(year): {'label': str(year), 'style': {'color': 'white', 'fontSize': '14px'}} for year in year_options},
                step=None,
                className="dark-slider"
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '5%'})
    ], style={'backgroundColor': '#444444', 'padding': '20px', 'color': 'white'})

def graphs_layout():
    return html.Div(id='graphs-container', style={'padding': '20px'})
