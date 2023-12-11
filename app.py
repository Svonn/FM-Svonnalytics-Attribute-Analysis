import os
from dash import Dash, html, dcc
import components
import callbacks

app = Dash(__name__)

directory = 'data/'
header_json_path = 'header.json'

def get_available_projects(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

projects = get_available_projects(directory)

position_options = []
attribute_options = []
year_options = []

# Setup app layout
app.layout = html.Div([
    components.selection_layout(projects, position_options, attribute_options, year_options),
    dcc.Loading(
            id="loading-1",
            type="cube",
            children=[
                    components.graphs_layout(),
                    dcc.Store(id='hidden-data-store')],
            style={'marginTop': '200px'},
        ),

])

# Register callbacks
callbacks.register_callbacks(app, directory, header_json_path)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
