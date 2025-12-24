import pandas as pd
import os
import json

INPUT_FOLDER = "excel_files"
OUTPUT_FOLDER = "json_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

REQUIRED_COLUMNS = [
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
    Header row is identified when the first non-empty cell is 'Host IP'
    (case-sensitive)
    """
    for idx, row in df.iterrows():
        for cell in row:
            if pd.notna(cell):
                if str(cell).strip() == "Host IP":
                    return idx
                break
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

    # Extract only required columns (case-sensitive)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing columns in {file}: {missing_cols}")
        continue

    df = df[REQUIRED_COLUMNS]

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Convert to JSON
    data = df.to_dict(orient="records")

    json_file = os.path.splitext(file)[0] + ".json"
    json_path = os.path.join(OUTPUT_FOLDER, json_file)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Converted: {file} → {json_file}")
