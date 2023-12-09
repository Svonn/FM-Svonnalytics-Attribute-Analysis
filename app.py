# app.py

import time
from dash import Dash, html
import components
import callbacks
from data_loader import load_all_data

app = Dash(__name__)

# Path to the header configuration and data directory
header_json_path = 'header.json'
directory = 'data/'

# Load data
print("Loading data...")
start_ts = time.time()
all_players_data = load_all_data(directory, header_json_path)
print(f"Data loaded in {time.time() - start_ts:.2f} seconds.")

# Prepare options for dropdowns
position_options = sorted(set(pos for sublist in all_players_data['Position'] for pos in sublist))
attribute_options = all_players_data.columns[12:55].tolist()  # Adjust the index as needed
year_options = sorted(all_players_data['Year'].unique().tolist())

# Setup app layout
app.layout = html.Div([
    components.selection_layout(position_options, attribute_options, year_options),
    components.graphs_layout()
])

# Register callbacks
callbacks.register_callbacks(app, all_players_data)

if __name__ == '__main__':
    app.run_server(debug=True)  # Set debug=True for development, False for production
