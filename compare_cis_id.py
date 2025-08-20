import json
import os

# Paths
cis_ids_file = "cis_ids.txt"   # text file with CIS IDs (one per line)
json_folder = "json_files"     # folder containing JSON files

# Load CIS IDs into a set
with open(cis_ids_file, "r") as f:
    cis_ids = {line.strip() for line in f if line.strip()}

print(f"Loaded {len(cis_ids)} CIS IDs from text file.")

matches = []

# Go through JSON files
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        with open(os.path.join(json_folder, filename), "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Skipping {filename}, invalid JSON: {e}")
                continue

            # If JSON is a list of CIS IDs
            if isinstance(data, list):
                for cis_id in data:
                    if cis_id in cis_ids:
                        matches.append((filename, cis_id))
            else:
                # Single CIS ID in the JSON
                if data in cis_ids:
                    matches.append((filename, data))

# Show results
if matches:
    print("\n✅ Matches found:")
    for file, cid in matches:
        print(f"File: {file} | CIS ID: {cid}")
else:
    print("\n❌ No matches found.")

--------------

import json
import os

# Paths
cis_ids_file = "cis_ids.txt"   # text file with CIS IDs (one per line)
json_folder = "json_files"     # folder containing JSON files

# Load CIS IDs into a set
with open(cis_ids_file, "r") as f:
    cis_ids = {line.strip() for line in f if line.strip()}

print(f"Loaded {len(cis_ids)} CIS IDs from text file.")

matches = []

# Iterate through JSON files
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        with open(os.path.join(json_folder, filename), "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Skipping {filename}, invalid JSON: {e}")
                continue

            if not isinstance(data, list):
                continue  # skip unexpected structure

            # Compare each entry
            for item in data:
                if (
                    item.get("platform") == "microsoft_windows_server_2022"
                    and item.get("id") in cis_ids
                ):
                    matches.append((filename, item["id"]))

# Print results
if matches:
    print("\n✅ Matches found:")
    for file, cid in matches:
        print(f"File: {file} | CIS ID: {cid}")
else:
    print("\n❌ No matches found.")
------

import json
import os

# Paths
cis_ids_file = "cis_ids.txt"   # text file with CIS IDs (one per line)
json_folder = "json_files"     # folder containing JSON files

# Load CIS IDs into a set
with open(cis_ids_file, "r") as f:
    cis_ids = {line.strip() for line in f if line.strip()}

print(f"Loaded {len(cis_ids)} CIS IDs from text file.")

matched_ids = set()

# Iterate through JSON files
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        with open(os.path.join(json_folder, filename), "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Skipping {filename}, invalid JSON: {e}")
                continue

            if not isinstance(data, list):
                continue  # skip unexpected structure

            # Compare each entry
            for item in data:
                if (
                    item.get("platform") == "microsoft_windows_server_2022"
                    and item.get("id") in cis_ids
                ):
                    matched_ids.add(item["id"])

# Results
print("\n✅ Unique Matches:")
for cid in sorted(matched_ids):
    print(cid)

print(f"\n📊 Matched {len(matched_ids)} out of {len(cis_ids)} CIS IDs from the text file.")
