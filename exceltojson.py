import os
import json
import math

JSON_FOLDER = "json_files"
BUNIT_VALUE = "awscentral_qualys"

def sanitize(obj):
    """
    Recursively:
    - Replace NaN / Inf with None
    - Add bunit to each JSON object (dict)
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, dict):
        # Add / overwrite bunit
        obj["bunit"] = BUNIT_VALUE
        return {k: sanitize(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize(item) for item in obj]

    return obj

for file in os.listdir(JSON_FOLDER):
    if not file.endswith(".json"):
        continue

    file_path = os.path.join(JSON_FOLDER, file)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clean_data = sanitize(data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=4)

    print(f"✅ Sanitized and updated: {file}")

---
import os
import json

WAIVER_FILE = "waivers.yaml"
JSON_FOLDER = "json_files"

# -----------------------------
# Load waivers (NO splitting)
# -----------------------------
waivers = set()

with open(WAIVER_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            waivers.add(line)

# -----------------------------
# Process JSON files
# -----------------------------
for file in os.listdir(JSON_FOLDER):
    if not file.endswith(".json"):
        continue

    file_path = os.path.join(JSON_FOLDER, file)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False

    for item in data:
        status = item.get("Status")
        control_ref = item.get("Control Reference")

        # Change ONLY if Status is Failed and exact match exists
        if status == "Failed" and control_ref in waivers:
            item["Status"] = "Skipped"
            updated = True

    if updated:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Updated: {file}")
    else:
        print(f"ℹ️ No changes: {file}")

---
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
