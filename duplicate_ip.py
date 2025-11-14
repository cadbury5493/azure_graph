
import pandas as pd

# ---- CONFIG ----
input_file = "input.csv"           # your file
output_file = "output_with_status.csv"
ip_column = "IP"                   # column name for IP address
time_column = "UpdatedTime"        # column name for updated time
# -----------------

# Load CSV
df = pd.read_csv(input_file)

# Convert time column to datetime
df[time_column] = pd.to_datetime(df[time_column], errors='coerce')

# Sort so the latest time comes first
df = df.sort_values(by=[ip_column, time_column], ascending=[True, False])

# Mark the first occurrence (latest) per IP as KEEP, others as DUPLICATE
df["Status"] = df.duplicated(subset=[ip_column], keep="first").map({
    False: "KEEP",
    True: "DUPLICATE"
})

# Save result
df.to_csv(output_file, index=False)

print("Done! Result saved to:", output_file)
