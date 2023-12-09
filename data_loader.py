from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import os
import json
import re

def load_headers(header_json_path):
    with open(header_json_path, 'r', encoding="utf-8") as f:
        return json.load(f)

year_pattern = re.compile(r'u16_(\d{4}).html')
position_pattern = re.compile(r'([A-Z/]+) ?\(([A-Z]+)\)')

def extract_year_from_filename(filename):
    match = year_pattern.search(filename)
    return int(match.group(1)) if match else None

def read_html_file(file_path, headers, year):
    try:
        data = pd.read_html(file_path, header=None, skiprows=[0], encoding="utf-8", keep_default_na=False, flavor='lxml')
        df = data[0]
        df.columns = headers
        df['Year'] = year
        return df
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def parse_positions(position_string):
    positions = position_string.split(', ')
    all_positions = []
    for position in positions:
        if '(' not in position:
            all_positions.append(position.strip())
            continue

        match = position_pattern.match(position)
        if match:
            field_position, locations = match.groups()
            field_positions = field_position.split('/')
            for fp in field_positions:
                for loc in locations:
                    all_positions.append(f'{fp}({loc})')
    return all_positions

def load_data_for_file(filename, directory, headers):
    year = extract_year_from_filename(filename)
    if year:
        file_path = os.path.join(directory, filename)
        df = read_html_file(file_path, headers, year)
        if df is not None:
            df['Position'] = df['Position'].apply(parse_positions)
            return df
    return None


def load_all_data(directory, header_json_path, max_workers=10, save_path='combined_data.pkl'):
    if os.path.exists(save_path):
        print(f"Loading data from {save_path}")
        return pd.read_pickle(save_path)

    headers = load_headers(header_json_path)
    all_data = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(load_data_for_file, filename, directory, headers) for filename in os.listdir(directory) if filename.endswith(".html")]
        for future in as_completed(futures):
            df = future.result()
            if df is not None:
                all_data.append(df)

    combined_data = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    combined_data.to_pickle(save_path)
    print(f"Data saved to {save_path}")
    return combined_data
