import re
import json
import pandas as pd
from markupsafe import Markup
from fetch_data import fetch_google_sheet, fetch_and_update_json, is_json_expired
from utils import format_price

def load_initial_data():
    global price_df, sheet_clean_df

    if is_json_expired():
        fetch_and_update_json()

    with open("auction_data.json") as f:
        auction_data = json.load(f)

    # Load prices to dataframe
    price_df = pd.DataFrame(auction_data)

    # Load the items.csv (needs SoD updates)
    items_df = pd.read_csv("items.csv")
    items_df['itemId'] = items_df['itemId'].astype(int)

    # Join items and prices
    price_df = price_df.join(items_df.set_index('itemId'), on='itemId', how='left')

    # Load Google Sheet Data
    worksheet_key = "1ahgy_WaKxFWhXpN-WJKVs58Y3jHQ8fM5pgdTH2X_vzg"
    worksheet_name = "Sheet5"
    sheet_data = fetch_google_sheet(worksheet_key, worksheet_name)

    print(f"Enchanting data loaded: {sheet_data.shape}")
    sheet_df = split_materials_column(sheet_data)
    sheet_clean_df = process_sheet_df(sheet_df, price_df)
    sheet_clean_df.replace({"TRUE": "Yes", "FALSE": "No"}, inplace=True)
    sheet_clean_df = sheet_clean_df.reset_index(drop=True)
    return sheet_clean_df  # Return the DataFrame

def process_sheet_df(sheet_df, price_df):
    sheet_df['Total Cost (Copper)'] = sheet_df.apply(calculate_cell_value, args=(price_df,), axis=1)
    sheet_df['Total Cost'] = sheet_df['Total Cost (Copper)'].apply(format_price)

    columns_to_keep = ['Enchant Name', 'Slot', 'Stats Given', 'Total Cost', 'Dunder', 'Leif',
                       'Dpsmage', 'Next phase', 'Materials']
    return sheet_df[columns_to_keep]


def parse_materials_column(materials_string):
    """
    Parses a string containing material quantities and names, extracting all items.

    Args:
        materials_string (str): The string to parse.

    Returns:
        dict: A dictionary with keys as material names and values as their quantities (integers).
    """
    materials_dict = {}
    items = materials_string.split(',')  # Split into individual items
    for item in items:
        match = re.search(r'(\d+)\s+(.*)', item.strip())
        if match:
            quantity = int(match.group(1))
            name = match.group(2)
            materials_dict[name] = quantity
    return materials_dict


def split_materials_column(sheet_df):
    """Splits the 'Materials' column into separate columns for each material."""
    for i, row in sheet_df.iterrows():
        materials_dict = parse_materials_column(row['Materials'])
        for material, quantity in materials_dict.items():
            sheet_df.loc[i, material] = quantity
    sheet_df.fillna(0, inplace=True)

    return sheet_df


def calculate_cell_value(row, price_df):
    """Calculates the total cost of materials for a single row (enchant recipe).

    Args:
        row: A single row from the sheet_df representing an enchant recipe.
        price_df: The DataFrame containing item names and prices.

    Returns:
        The total cost of the materials in copper."""

    total_cost_copper = 0  # Calculate the total cost in copper

    for index, value in row.items():
        if pd.isna(value) or value == 0:
            continue

        item_name = index
        quantity = value

        try:
            price_copper = price_df.loc[price_df['itemName'] == item_name, 'minBuyout'].iloc[0]
            total_cost_copper += price_copper * quantity
        except IndexError:
            pass
    return int(total_cost_copper)


def process_materials(materials_string):
    formatted_materials = re.sub(r', ?', '<br>', materials_string)  # Replace commas with <br> tags
    return Markup(formatted_materials)