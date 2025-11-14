import pandas as pd

# -------------------------------
# CONFIG
cmdb_file = "cmdb.csv"
azure_file = "azure.csv"

name_column = "Name"   # column name in BOTH CSVs
output_file = "comparison_output.csv"
# -------------------------------

# Load CSVs
cmdb = pd.read_csv(cmdb_file)
azure = pd.read_csv(azure_file)

# Normalize case (lowercase names for comparison)
cmdb["_name_lower"] = cmdb[name_column].astype(str).str.lower().str.strip()
azure["_name_lower"] = azure[name_column].astype(str).str.lower().str.strip()

# ---- Determine membership ----
cmdb_set = set(cmdb["_name_lower"])
azure_set = set(azure["_name_lower"])

# ---- Build unified list of all names ----
all_names = pd.DataFrame({"_name_lower": list(cmdb_set | azure_set)})

# Merge original data for reference
all_names = all_names.merge(azure, on="_name_lower", how="left", suffixes=("", "_azure"))
all_names = all_names.merge(cmdb, on="_name_lower", how="left", suffixes=("_azure", "_cmdb"))

# ---- Determine status for each row ----
def compute_status(row):
    in_azure = pd.notna(row[name_column])
    in_cmdb = pd.notna(row[name_column + "_cmdb"])
    
    if in_azure and in_cmdb:
        return "match_in_azure_and_cmdb"
    elif in_azure and not in_cmdb:
        return "in_azure_not_in_cmdb"
    else:
        return "in_cmdb_not_in_azure"

all_names["Status"] = all_names.apply(compute_status, axis=1)

# Output
all_names.to_csv(output_file, index=False)
print("Done! Output saved to:", output_file)
