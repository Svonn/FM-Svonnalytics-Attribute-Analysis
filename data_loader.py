from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import pandas as pd
import os
import json
import re
from tqdm import tqdm

def load_headers(header_json_path):
    with open(header_json_path, 'r', encoding="utf-8") as f:
        return json.load(f)

year_pattern = re.compile(r'.*(\d{4}).*.html')
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


def can_convert_to_numeric(column):
    # Placeholder function for checking if a column can be converted to numeric
    try:
        pd.to_numeric(column)
        return True
    except ValueError:
        return False

def read_html_in_chunks(file_path, headers, year, chunk_size=1000):
    try:
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find individual table rows
        rows = re.findall(r'<tr.*?/tr>', content, re.DOTALL)

        # Skip the first row if it's a header
        rows = rows[1:]

        # Process the rows in chunks
        dfs = []
        for i in tqdm(range(0, len(rows), chunk_size), desc="Processing Chunks"):
            chunk = ''.join(rows[i:i + chunk_size])
            chunk = f'<table>{chunk}</table>'
            chunk_io = io.StringIO(chunk)

            df = pd.read_html(chunk_io, header=None, keep_default_na=False, flavor='lxml')[0]
            df.columns = headers
            df['Year'] = year
            dfs.append(df)

        # Concatenate all dataframes without retaining the original index
        final_df = pd.concat(dfs, ignore_index=True)
        
        for column in final_df.select_dtypes(include=['object']).columns:
            if can_convert_to_numeric(final_df[column]):
                final_df[column] = pd.to_numeric(final_df[column])

        return final_df

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
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

def load_data_for_file(filename, project_directory, headers):
    year = extract_year_from_filename(filename)
    if year:
        file_path = os.path.join(project_directory, filename)
        df = read_html_in_chunks(file_path, headers, year)
        if df is not None:
            df['Position'] = df['Position'].apply(parse_positions)
            return df
    return None

def load_all_data(project, base_directory, header_json_path, max_workers=10):
    project_directory = os.path.join(base_directory, project)
    save_path = os.path.join(project_directory, 'combined_data.pkl')

    if os.path.exists(save_path):
        df = pd.read_pickle(save_path)
        print(f"Using data from {save_path}")
        return df

    headers = load_headers(header_json_path)
    all_data = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(load_data_for_file, filename, project_directory, headers) 
                   for filename in os.listdir(project_directory) if filename.endswith(".html")]

        for future in as_completed(futures):
            df = future.result()
            if df is not None:
                print(f"Loaded {df.shape[0]} rows from {df['Year'].iloc[0]}")
                all_data.append(df)

    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.to_pickle(save_path)
        print(f"Data saved to {save_path}")
        return combined_data
    else:
        print("No data loaded")
        raise Exception("No data loaded")