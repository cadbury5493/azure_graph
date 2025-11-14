import pandas as pd

# Load CSVs
cmdb = pd.read_csv("cmdb.csv")
azure = pd.read_csv("azure.csv")

# Normalize case
cmdb["_name_lower"] = cmdb["Name"].astype(str).str.lower().str.strip()
azure["_name_lower"] = azure["Name"].astype(str).str.lower().str.strip()

# Create sets for comparison
cmdb_set = set(cmdb["_name_lower"])
azure_set = set(azure["_name_lower"])

# Assign Status
cmdb["Status"] = cmdb["_name_lower"].apply(lambda x: "match_in_azure_and_cmdb" if x in azure_set else "in_cmdb_not_in_azure")
azure["Status"] = azure["_name_lower"].apply(lambda x: "match_in_azure_and_cmdb" if x in cmdb_set else "in_azure_not_in_cmdb")

# Combine both datasets
combined = pd.concat([cmdb, azure], ignore_index=True)

# Drop helper column
combined = combined.drop(columns=["_name_lower"])

# Save final CSV
combined.to_csv("comparison_output.csv", index=False)

# Print counts
print("Total CMDB records:", len(cmdb))
print("Total Azure records:", len(azure))
print("Matches in CMDB:", sum(cmdb["Status"]=="match_in_azure_and_cmdb"))
print("Matches in Azure:", sum(azure["Status"]=="match_in_azure_and_cmdb"))
