import pandas as pd

# -------------------------------
cmdb_file = "cmdb.csv"
azure_file = "azure.csv"
name_column = "Name"   # Column to compare
output_file = "comparison_output.csv"
# -------------------------------

# Load CSVs
cmdb = pd.read_csv(cmdb_file)
azure = pd.read_csv(azure_file)

# Remove leading/trailing spaces from column names
cmdb.columns = cmdb.columns.str.strip()
azure.columns = azure.columns.str.strip()

# Normalize names to lowercase for case-insensitive comparison
cmdb["_name_lower"] = cmdb[name_column].astype(str).str.lower().str.strip()
azure["_name_lower"] = azure[name_column].astype(str).str.lower().str.strip()

# Add source tags
cmdb["source"] = "cmdb"
azure["source"] = "azure"

# Combine datasets
combined = pd.concat([cmdb, azure], ignore_index=True)

# Count occurrences of each hostname
combined["count"] = combined.groupby("_name_lower")["_name_lower"].transform("count")

# Determine status
def get_status(row):
    if row["count"] > 1:
        return "match_in_azure_and_cmdb"
    elif row["source"] == "azure":
        return "in_azure_not_in_cmdb"
    else:
        return "in_cmdb_not_in_azure"

combined["Status"] = combined.apply(get_status, axis=1)

# Drop helper columns
combined = combined.drop(columns=["_name_lower", "count", "source"])

# Save final CSV
combined.to_csv(output_file, index=False)
print("Comparison done! Output saved to:", output_file)
