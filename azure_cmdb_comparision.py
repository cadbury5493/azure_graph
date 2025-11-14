import pandas as pd

# -------------------------------
cmdb_file = "cmdb.csv"
azure_file = "azure.csv"
name_column = "Name"   # Column to compare
output_file = "comparison_unique.csv"
# -------------------------------

# Load CSVs
cmdb = pd.read_csv(cmdb_file)
azure = pd.read_csv(azure_file)

# Normalize names to lowercase and strip spaces
cmdb["_name_lower"] = cmdb[name_column].astype(str).str.lower().str.strip()
azure["_name_lower"] = azure[name_column].astype(str).str.lower().str.strip()

# Drop duplicates based on Name
cmdb_unique = cmdb.drop_duplicates(subset=["_name_lower"])
azure_unique = azure.drop_duplicates(subset=["_name_lower"])

# Create sets for unique names
cmdb_set = set(cmdb_unique["_name_lower"])
azure_set = set(azure_unique["_name_lower"])

# Union of all unique hostnames
all_hosts = pd.DataFrame({"_name_lower": list(cmdb_set | azure_set)})

# Determine Status for each unique hostname
def get_status(name):
    if name in cmdb_set and name in azure_set:
        return "match_in_azure_and_cmdb"
    elif name in azure_set:
        return "in_azure_not_in_cmdb"
    else:
        return "in_cmdb_not_in_azure"

all_hosts["Status"] = all_hosts["_name_lower"].apply(get_status)

# Optional: keep original casing from CMDB if available, otherwise Azure
def get_original_name(name):
    if name in cmdb_set:
        return cmdb_unique.loc[cmdb_unique["_name_lower"] == name, name_column].values[0]
    else:
        return azure_unique.loc[azure_unique["_name_lower"] == name, name_column].values[0]

all_hosts["Name"] = all_hosts["_name_lower"].apply(get_original_name)

# Reorder columns
all_hosts = all_hosts[["Name", "Status"]]

# Save output
all_hosts.to_csv(output_file, index=False)
print("Done! Output saved to:", output_file)
print("Total unique hosts:", len(all_hosts))
print("Matches:", sum(all_hosts["Status"]=="match_in_azure_and_cmdb"))
print("In Azure only:", sum(all_hosts["Status"]=="in_azure_not_in_cmdb"))
print("In CMDB only:", sum(all_hosts["Status"]=="in_cmdb_not_in_azure"))
