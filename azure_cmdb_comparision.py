import pandas as pd

# ---------------------------------
# CONFIG
cmdb_file = "cmdb.xlsx"
azure_file = "azure_hosts.xlsx"

cmdb_name_col = "Name"     # column name in CMDB
azure_name_col = "Name"    # column name in Azure hosts

output_prefix = "comparison_output"
# ---------------------------------

# Load both files
cmdb = pd.read_excel(cmdb_file)
azure = pd.read_excel(azure_file)

# Normalize hostnames to lowercase for comparison
cmdb["__name_lower__"] = cmdb[cmdb_name_col].astype(str).str.lower().str.strip()
azure["__name_lower__"] = azure[azure_name_col].astype(str).str.lower().str.strip()

# --- 1) MATCHES IN BOTH ---
matches = pd.merge(
    azure, cmdb,
    on="__name_lower__", 
    suffixes=("_azure", "_cmdb"),
    how="inner"
)
matches["status"] = "match_in_azure_and_cmdb"

# --- 2) IN AZURE BUT NOT IN CMDB ---
azure_only = azure[~azure["__name_lower__"].isin(cmdb["__name_lower__"])]
azure_only["status"] = "in_azure_not_in_cmdb"

# --- 3) IN CMDB BUT NOT IN AZURE ---
cmdb_only = cmdb[~cmdb["__name_lower__"].isin(azure["__name_lower__"])]
cmdb_only["status"] = "in_cmdb_not_in_azure"

# Save results to Excel files
matches.to_excel(f"{output_prefix}_matches.xlsx", index=False)
azure_only.to_excel(f"{output_prefix}_azure_only.xlsx", index=False)
cmdb_only.to_excel(f"{output_prefix}_cmdb_only.xlsx", index=False)

print("Comparison completed!")
print("Files created:")
print(f" - {output_prefix}_matches.xlsx")
print(f" - {output_prefix}_azure_only.xlsx")
print(f" - {output_prefix}_cmdb_only.xlsx")
