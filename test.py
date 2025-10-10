import os
import re

# Define account ID to environment mapping
account_env_map = {
    "045343430433": "prod",
    "123456789012": "dev",
    "987654321098": "uat"
}

# Directory where your CSV files are stored
directory = "./"  # change this if needed

# Regex to extract region and account ID from the filename
pattern = re.compile(r"InspectorCISScanReport_(?P<region>[^_]+)_(?P<account_id>\d+)_")

for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        match = pattern.search(filename)
        if match:
            region = match.group("region")
            account_id = match.group("account_id")

            if account_id in account_env_map:
                env = account_env_map[account_id]
                new_name = f"{env}_{region}.csv"
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)

                # Rename file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} → {new_name}")
            else:
                print(f"Skipped (unknown account): {filename}")

----
import os
import csv
import json
from datetime import datetime

input_folder = "path_to_folder_with_csvs"  # change to your folder path
environment = "uat"

for file in os.listdir(input_folder):
    if not file.endswith(".csv"):
        continue

    filepath = os.path.join(input_folder, file)
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    if len(reader) < 3:
        print(f"Skipping {file} - not enough rows")
        continue

    # Row 1 → account_id
    account_id = str(reader[0][0]).replace("#account_id:", "").strip()

    # Row 2 → scan details
    scan_arn = str(reader[1][0]).replace("#scan_arn:", "").strip()
    scan_config_arn = str(reader[1][1]).replace("scan_configuration_arn:", "").strip()
    resource_tags = str(reader[1][5]).replace("resource_tags:", "").strip()

    # Row 3 → check if not_evaluated_resources exists
    not_eval_data = str(reader[2][0])
    if not not_eval_data.startswith("#not_evaluated_resources:"):
        print(f"Skipping {file} - no not_evaluated_resources")
        continue

    # Parse resources
    resources_str = not_eval_data.replace("#not_evaluated_resources:", "").strip()
    resources = [r.strip() for r in resources_str.split(",") if r.strip()]

    output_data = []
    for res in resources:
        arn_parts = res.split(":")
        region = arn_parts[3]
        instance_id = res.split("/")[-1].split(":")[0]
        status = res.split(":")[-1]

        entry = {
            "host_name": f"Name@{instance_id}",
            "account_id": account_id,
            "scan_arn": scan_arn,
            "scan_config_arn": scan_config_arn,
            "resource_tags": resource_tags,
            "status": status,
            "region": region,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "exec_mode": "weekly_cis_awscentral_not_evaluated",
            "bunit": "awscentral",
            "environment": environment
        }
        output_data.append(entry)

    # Save JSON per region
    output_filename = f"{environment}_{region}_not_evaluated.json"
    output_path = os.path.join(input_folder, output_filename)


for f in nonprod_*.csv; do mv "$f" "dev_${f#nonprod_}"; done; for f in nonprod2_*.csv; do mv "$f" "uat_${f#nonprod2_}"; done

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved {output_filename} with {len(output_data)} entries")
