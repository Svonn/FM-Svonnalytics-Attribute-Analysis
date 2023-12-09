from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objs as go
import utils

def register_callbacks(app, all_players_data):
    @app.callback(
        Output('graphs-container', 'children'),  # Assuming you have a container for graphs in your layout
        [Input('position-dropdown', 'value'),
         Input('attribute-dropdown', 'value'),
         Input('year-range-slider', 'value')]
    )
    def update_dashboard(selected_positions, selected_attributes, selected_years):
        print("Updating dashboard...")  # Diagnostic print
        print(f"Selected positions: {selected_positions}")
        print(f"Selected attributes: {selected_attributes}")
        print(f"Selected years: {selected_years}")
        # Filter data based on selections
        filtered_data = all_players_data[all_players_data['Year'].between(selected_years[0], selected_years[1])]

        if selected_positions:
            filtered_data = filtered_data[filtered_data['Position'].apply(lambda x: any(pos in x for pos in selected_positions))]
            
        print(f"Filtered data size: {len(filtered_data)}")  # Check if data is filtered correctly

        # Create a list to store the graph components
        graphs = []

        # Special handling for Current Ability
        ca_attribute = 'Current Ability'  # Adjust the attribute name as per your data
        graphs.extend(create_attribute_graphs(filtered_data, ca_attribute, selected_years, is_ca=True))
        # Generate graphs for other selected attributes
        for attribute in selected_attributes:
            graphs.extend(create_attribute_graphs(filtered_data, attribute, selected_years))
        return graphs

def create_attribute_graphs(data, attribute, years, is_ca=False):
    """
    Create a row of graphs for a given attribute, with titles.
    """
    row = html.Div([
        html.H2(f"{attribute}", style={'textAlign': 'center'}),
        html.Div([
            dcc.Graph(figure=utils.generate_box_plot(data, attribute, [years[0], years[-1]], title=f"{attribute} Box Plot (First vs Last Year)"), style={'flex': 1}),
            dcc.Graph(figure=utils.generate_line_chart(data, attribute, ca_column='Current Ability' if not is_ca else None, title=f"{attribute} Mean Over Years"), style={'flex': 1}),
            dcc.Graph(figure=utils.generate_combined_histogram_kde(data, attribute, [years[0], years[-1]], title=f"{attribute} Histogram & KDE (First and Last Year)"), style={'flex': 1})
        ], style={'display': 'flex', 'flexDirection': 'row'})
    ], style={
        'marginBottom': '10px',
        'border': '1px solid #DDD',
        'boxShadow': '0px 0px 10px 0px rgba(200, 200, 200, 0.5)',
        'padding': '10px',
        'backgroundColor': 'white'
    })
    return [row]
