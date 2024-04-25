import os
import time
from flask import Flask, render_template, request, jsonify
from fetch_data import fetch_and_update_json, is_json_expired, update_data_background
from data_processing import load_initial_data, process_materials

app = Flask(__name__)

@app.route("/")
def main_list():
    return render_template("index.html",
                           enumerate=enumerate)

@app.route('/get_table_data', methods=['GET'])  # Add GET support
def get_table_data():
    slot_filter = request.args.get('slot')
    stats_filter = request.args.get('stats')
    print("Received slot_filter:", slot_filter, type(slot_filter))
    print("Received stats_filter:", stats_filter, type(stats_filter))

    if slot_filter:
        slot_filter = str(slot_filter)
    if stats_filter:
        stats_filter = str(stats_filter)
    filtered_df = sheet_clean_df.copy()  # Start with a fresh copy of the DataFrame
    filtered_df['Materials'] = filtered_df['Materials'].apply(process_materials)  # Apply the transformation

    if slot_filter:
        filtered_df = filtered_df[filtered_df['Slot'] == slot_filter]
    if stats_filter:
        filtered_df = filtered_df[filtered_df['Stats Given'] == stats_filter]

    column_headers = filtered_df.columns.tolist()  # Extract column headers
    table_data = filtered_df.values.tolist()  # Extract data as a list of rows

    # Find column index for Next Phase to use filtering
    column_index = filtered_df.columns.get_loc("Next phase")  # Calculate column index

    # Show time since last data update
    file_mod_time = os.path.getmtime("auction_data.json")
    current_time = time.time()
    file_age_minutes = int((current_time - file_mod_time) / 60)

    # Pass column widths
    column_widths = ["col-2", "col-1", "col-1", "col-1", "col-1", "col-1", "col-1", "col-1"]

    return render_template("table.html", column_headers=column_headers, table_data=table_data,
                           file_age_minutes=file_age_minutes, column_index=column_index, column_widths=column_widths,
                           enumerate=enumerate)


@app.route('/get_slots')
def get_slots():
    unique_slots = sheet_clean_df['Slot'].unique().tolist()
    return jsonify(unique_slots)


@app.route('/get_stats_for_slot/<slot_name>')
def get_stats_for_slot(slot_name):
    filtered_df = sheet_clean_df[sheet_clean_df['Slot'] == slot_name]
    unique_stats = filtered_df['Stats Given'].unique().tolist()
    return jsonify(unique_stats)


if __name__ == "__main__":
    sheet_clean_df = load_initial_data()
    update_data_background()
    app.run(debug=True, port=5001)
