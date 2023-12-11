from dash import dcc, html, Input, Output, State
import pandas as pd
from data_loader import load_all_data
import utils
from io import StringIO

def register_callbacks(app, directory, header_json_path):
    @app.callback(
        Output('graphs-container', 'children'),
        [Input('position-dropdown', 'value'),
        Input('attribute-dropdown', 'value'),
        Input('year-range-slider', 'value'),
        State('project-dropdown', 'value'),
        State('hidden-data-store', 'data')]  # Add this state
    )
    def update_dashboard(selected_positions, selected_attributes, selected_years, selected_project, stored_data):
        if not selected_project or not stored_data:
            return html.Div("Please select a project.")

        all_players_data = pd.read_json(StringIO(stored_data), orient='split')

        filtered_data = all_players_data[all_players_data['Year'].between(selected_years[0], selected_years[1])]
        if selected_positions:
            filtered_data = filtered_data[filtered_data['Position'].apply(lambda x: any(pos in x for pos in selected_positions))]
        
        graphs = []
        for attribute in selected_attributes:
            overall_stats = attribute.split(' ')[-1]    
            if not overall_stats.isdigit():
                overall_stats = None
            else:
                overall_stats = int(overall_stats)
            graphs.extend(create_attribute_graphs(filtered_data, attribute, selected_years, overall_stats=overall_stats))
        
        return graphs
    
    @app.callback(
        [Output('position-dropdown', 'options'),
        Output('attribute-dropdown', 'options'),
        Output('attribute-dropdown', 'value'),
        Output('year-range-slider', 'min'),
        Output('year-range-slider', 'max'),
        Output('year-range-slider', 'marks'),
        Output('year-range-slider', 'value'),
        Output('hidden-data-store', 'data')],
        [Input('project-dropdown', 'value'),
         Input('attribute-dropdown', 'value')]
    )
    def update_options(selected_project, selected_attributes):
        if not selected_project:
            return [], [], [],0, 1, {0: {'label': 'start', 'style': {'color': 'white', 'fontSize': '14px'}}, 1: {'label': 'end', 'style': {'color': 'white', 'fontSize': '14px'}}}, [0, 1], None

        print(f"Loading project: {selected_project}")
        all_players_data = load_all_data(selected_project, directory, header_json_path)

        position_options = [{'label': pos, 'value': pos} for pos in sorted(set(pos for sublist in all_players_data['Position'] for pos in sublist))]
        attribute_options = [{'label': attr, 'value': attr} for attr in all_players_data.columns[12:55].tolist()]
        year_options = {year: {'label': str(year), 'style': {'color': 'white', 'fontSize': '14px'}} for year in sorted(all_players_data['Year'].unique().tolist())}

        attribute_options.append({'label': 'Overall Stats 1', 'value': 'Overall Stats 1'})
        attribute_options.append({'label': 'Overall Stats 2', 'value': 'Overall Stats 2'})

        min_year, max_year = min(all_players_data['Year']), max(all_players_data['Year'])
        selected_attributes = selected_attributes or ["Overall Stats 1", "Overall Stats 2"]
        return position_options, attribute_options, selected_attributes, min_year, max_year, year_options, [min_year, max_year], all_players_data.to_json(date_format='iso', orient='split')


def create_attribute_graphs(data, attribute, years, overall_stats=False):
    title = f"{attribute}"
    if overall_stats == 1:
        attribute = "Current Ability"
        title = "Overall Stats 1"
    elif overall_stats == 2:
        attribute = "Potential Ability"
        title = "Overall Stats 2"
    row = html.Div([
        html.H2(title, style={'textAlign': 'center'}),
        html.Div([
            dcc.Graph(figure=utils.generate_box_plot(data, attribute, [years[0], years[-1]], title=f"{attribute} Box Plot (First vs Last Year)"), style={'flex': 1}),
            dcc.Graph(figure=utils.generate_line_chart(data, attribute, overall_stats=overall_stats), style={'flex': 1}),
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
