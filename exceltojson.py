import pandas as pd
import os
import json
import re

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

IP_REGEX = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$|^[a-zA-Z0-9.-]+$"
)

def find_header_row(df):
    for idx, row in df.iterrows():
        for cell in row:
            if pd.notna(cell):
                if str(cell).strip() == "Host IP":
                    return idx
                break
    return None

def is_valid_data_row(row):
    """
    Determines whether a row is real data or garbage
    """
    host_ip = str(row.get("Host IP", "")).strip()
    control_id = str(row.get("Control ID", "")).strip()

    # Skip empty rows
    if not host_ip and not control_id:
        return False

    # Skip repeated header rows
    if host_ip == "Host IP":
        return False

    # Control ID must exist
    if not control_id:
        return False

    # Host IP must look valid
    if not IP_REGEX.match(host_ip):
        return False

    return True

for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".xlsx"):
        continue

    file_path = os.path.join(INPUT_FOLDER, file)

    raw_df = pd.read_excel(file_path, header=None)
    header_row_index = find_header_row(raw_df)

    if header_row_index is None:
        print(f"⚠️ Header row not found in {file}")
        continue

    df = pd.read_excel(file_path, header=header_row_index)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing columns in {file}: {missing_cols}")
        continue

    df = df[REQUIRED_COLUMNS]

    # 🔥 FILTER OUT GARBAGE ROWS
    df = df[df.apply(is_valid_data_row, axis=1)]

    # Convert to JSON
    data = df.to_dict(orient="records")

    json_file = os.path.splitext(file)[0] + ".json"
    json_path = os.path.join(OUTPUT_FOLDER, json_file)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Converted: {file} → {json_file}")
