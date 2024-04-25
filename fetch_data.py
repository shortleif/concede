import pandas as pd
import requests
import time
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from threading import Timer  # Import for background updates

TSM_API_KEY = os.environ.get("tsm_key")

auth = {
    "client_id": "c260f00d-1071-409a-992f-dda2e5498536",
    "grant_type": "api_token",
    "scope": "app:realm-api app:pricing-api",
    "token": TSM_API_KEY
}


def fetch_google_sheet(worksheet_key, worksheet_name):
    """Fetches data from a Google Sheet and returns a DataFrame."""

    # Authentication
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    credentials_dict = json.loads(credentials_json)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

    gc = gspread.authorize(credentials)

    # Fetch data
    workbook = gc.open_by_key(worksheet_key)
    worksheet = workbook.worksheet(worksheet_name)
    data = worksheet.get_all_records()  # Fetch data as a list of dictionaries

    # Create DataFrame
    google_df = pd.DataFrame(data)
    return google_df


if __name__ == "__main__":
    # Your worksheet details
    worksheet_key = "1ahgy_WaKxFWhXpN-WJKVs58Y3jHQ8fM5pgdTH2X_vzg"
    worksheet_name = "Sheet5"

    # Fetch and Transform
    df = fetch_google_sheet(worksheet_key, worksheet_name)
    print(df)


# Refresh JSON if it's older than 15 minutes
UPDATE_THRESHOLD = 15 * 60  # 15 minutes in seconds


def fetch_and_update_json():
    response = requests.post("https://auth.tradeskillmaster.com/oauth2/token", auth)
    print(f"Access_token received: {response}")
    access_token_tsm = response.json().get("access_token")

    headers = {'Authorization': f'Bearer {access_token_tsm}'}

    auction_data = requests.get("https://pricing-api.tradeskillmaster.com/ah/512", headers=headers).json()

    with open("auction_data.json", "w") as f:
        json.dump(auction_data, f)

    global price_df
    price_df = pd.DataFrame(auction_data)


def is_json_expired():
    if not os.path.exists("auction_data.json"):
        return True  # File doesn't exist, needs updating

    file_mod_time = os.path.getmtime("auction_data.json")
    current_time = time.time()
    return current_time - file_mod_time > UPDATE_THRESHOLD


def update_data_background():
    if is_json_expired():
        fetch_and_update_json()

    # Schedule this function to run again after a set interval
    Timer(UPDATE_THRESHOLD, update_data_background).start()
