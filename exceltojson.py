import pandas as pd
import os
import json

INPUT_FOLDER = "excel_files"
OUTPUT_FOLDER = "json_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Required headers to detect
REQUIRED_HEADERS = [
    "Host IP",
    "DNS Host",
    "Operating System",
    "Control ID",
    "Control Reference",
    "Technology",
    "Control",
    "Rationale",
    "Status",
    "Remediation",
    "Evidence"
]

def find_header_row(df):
    """
    Finds the row index that contains all required headers
    """
    for idx, row in df.iterrows():
        row_values = row.astype(str).str.strip().tolist()
        if all(header in row_values for header in REQUIRED_HEADERS):
            return idx
    return None

for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".xlsx"):
        continue

    file_path = os.path.join(INPUT_FOLDER, file)

    # Read without headers
    raw_df = pd.read_excel(file_path, header=None)

    header_row_index = find_header_row(raw_df)

    if header_row_index is None:
        print(f"⚠️ Header row not found in {file}")
        continue

    # Read again using detected header row
    df = pd.read_excel(file_path, header=header_row_index)

    # Keep only required columns (order preserved)
    df = df[REQUIRED_HEADERS]

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Convert to JSON
    data = df.to_dict(orient="records")

    json_file = os.path.splitext(file)[0] + ".json"
    json_path = os.path.join(OUTPUT_FOLDER, json_file)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Converted: {file} → {json_file}")
