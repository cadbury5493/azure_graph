import pandas as pd
import os
import json

# Folder containing xlsx files
INPUT_FOLDER = "excel_files"
OUTPUT_FOLDER = "json_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file in os.listdir(INPUT_FOLDER):
    if file.endswith(".xlsx"):
        file_path = os.path.join(INPUT_FOLDER, file)

        # Read Excel file (first sheet by default)
        df = pd.read_excel(file_path)

        # Convert to list of dicts (header row = keys)
        data = df.to_dict(orient="records")

        # Output JSON filename
        json_file = os.path.splitext(file)[0] + ".json"
        json_path = os.path.join(OUTPUT_FOLDER, json_file)

        # Write JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Converted: {file} → {json_file}")
