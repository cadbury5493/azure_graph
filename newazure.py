import pandas as pd

# -------------------------------
cmdb_file = "cmdb.csv"
azure_file = "azure.csv"
name_column = "Name"
output_file = "comparison_unique.csv"
# -------------------------------

# Load CSVs
cmdb = pd.read_csv(cmdb_file)
azure = pd.read_csv(azure_file)

# Normalize names
cmdb["_name_lower"] = cmdb[name_column].astype(str).str.lower().str.strip()
azure["_name_lower"] = azure[name_column].astype(str).str.lower().str.strip()

# Drop duplicates
cmdb_unique = cmdb.drop_duplicates(subset=["_name_lower"])
azure_unique = azure.drop_duplicates(subset=["_name_lower"])

# Merge while keeping all data
merged = pd.merge(
    cmdb_unique,
    azure_unique,
    on="_name_lower",
    how="outer",
    suffixes=("_cmdb", "_azure")
)

# Determine status
def get_status(row):
    in_cmdb = not pd.isna(row.get(name_column + "_cmdb"))
    in_azure = not pd.isna(row.get(name_column + "_azure"))
    if in_cmdb and in_azure:
        return "match_in_azure_and_cmdb"
    elif in_azure:
        return "in_azure_not_in_cmdb"
    else:
        return "in_cmdb_not_in_azure"

merged["Status"] = merged.apply(get_status, axis=1)

# Pick better name (prefer CMDB)
merged["Name"] = merged[name_column + "_cmdb"].combine_first(
    merged[name_column + "_azure"]
)

# Reorder (Name + Status first)
cols = ["Name", "Status"] + [c for c in merged.columns if c not in ("Name","Status")]
final_df = merged[cols]

# Save output
final_df.to_csv(output_file, index=False)

print("Done! Output saved to:", output_file)
print("Total unique hosts:", len(final_df))
print("Matches:", sum(final_df["Status"]=="match_in_azure_and_cmdb"))
print("In Azure only:", sum(final_df["Status"]=="in_azure_not_in_cmdb"))
print("In CMDB only:", sum(final_df["Status"]=="in_cmdb_not_in_azure"))
