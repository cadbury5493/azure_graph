import pandas as pd
import os
import json

INPUT_FOLDER = "excel_files"
OUTPUT_FOLDER = "json_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

REQUIRED_HEADERS = {
    "host ip",
    "dns host",
    "operating system",
    "control id",
    "control reference",
    "technology",
    "control",
    "rationale",
    "status",
    "remediation",
    "evidence"
}

def find_header_row(df):
    """
    Finds row index where ALL required headers are present
    (extra columns allowed)
    """
    for idx, row in df.iterrows():
        row_values = {
            str(cell).strip().lower()
            for cell in row
            if pd.notna(cell)
        }

        if REQUIRED_HEADERS.issubset(row_values):
            return idx

    return None

for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".xlsx"):
        continue

    file_path = os.path.join(INPUT_FOLDER, file)

    # Read entire sheet without headers
    raw_df = pd.read_excel(file_path, header=None)

    header_row_index = find_header_row(raw_df)

    if header_row_index is None:
        print(f"⚠️ Header row not found in {file}")
        continue

    # Read again using detected header row
    df = pd.read_excel(file_path, header=header_row_index)

    # Normalize column names for safe selection
    df.columns = [str(col).strip() for col in df.columns]

    # Extract only required columns (ignore extras)
    required_columns_map = {
        col: col.strip()
        for col in df.columns
        if col.strip().lower() in REQUIRED_HEADERS
    }

    df = df[list(required_columns_map.keys())]

    # Drop fully empty rows
    df = df.dropna(how="all")

    # Convert to JSON
    data = df.to_dict(orient="records")

    json_file = os.path.splitext(file)[0] + ".json"
    json_path = os.path.join(OUTPUT_FOLDER, json_file)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Converted: {file} → {json_file}")
