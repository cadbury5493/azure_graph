import requests
import json
import time

# Tower/AWX details
TOWER_HOST = "https://your-tower-host"
BEARER_TOKEN = "your-api-token"

# Job template name (as shown in Tower UI)
JOB_TEMPLATE_NAME = "Install Nginx"

# Dynamic launch parameters
SCM_BRANCH = "feature-branch"
JOB_TAGS = "install,configure"
INVENTORY_ID = 5   # can also fetch dynamically if needed

# Extra vars
extra_vars = {
    "environment": "dev",   # your requested environment var
    "package_name": "nginx",
    "state": "latest"
}

# API headers with bearer token
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# 1️⃣ Get job template ID dynamically by name
search_url = f"{TOWER_HOST}/api/v2/job_templates/?name={JOB_TEMPLATE_NAME}"
resp = requests.get(search_url, headers=HEADERS, verify=False)

if resp.status_code != 200:
    raise Exception(f"Failed to search job template: {resp.status_code} {resp.text}")

results = resp.json().get("results", [])
if not results:
    raise Exception(f"No job template found with name: {JOB_TEMPLATE_NAME}")

job_template_id = results[0]["id"]
print(f"✅ Found job template '{JOB_TEMPLATE_NAME}' with ID {job_template_id}")

# 2️⃣ Launch the job with dynamic params
launch_url = f"{TOWER_HOST}/api/v2/job_templates/{job_template_id}/launch/"

payload = {
    "scm_branch": SCM_BRANCH,
    "job_tags": JOB_TAGS,
    "inventory": INVENTORY_ID,
    "extra_vars": extra_vars
}

response = requests.post(
    launch_url,
    headers=HEADERS,
    data=json.dumps(payload),
    verify=False
)

if response.status_code != 201:
    raise Exception(f"Failed to launch job: {response.status_code} {response.text}")

job = response.json()
job_id = job["id"]
print(f"🚀 Job launched! ID: {job_id}")

# 3️⃣ Poll job status
job_url = f"{TOWER_HOST}/api/v2/jobs/{job_id}/"

while True:
    job_resp = requests.get(job_url, headers=HEADERS, verify=False)
    if job_resp.status_code != 200:
        raise Exception(f"Failed to get job status: {job_resp.status_code} {job_resp.text}")

    job_data = job_resp.json()
    status = job_data["status"]
    print(f"Job {job_id} status: {status}")

    if status in ["successful", "failed", "error", "canceled"]:
        break

    time.sleep(5)

# 4️⃣ Final result
if status == "successful":
    print(f"Job {job_id} completed successfully")
else:
    print(f"Job {job_id} ended with status: {status}")

----


import requests
import json
import time
import re

# Tower/AWX details
TOWER_HOST = "https://your-tower-host"
BEARER_TOKEN = "your-api-token"

# Job template name (as shown in Tower UI)
JOB_TEMPLATE_NAME = "Install Nginx"

# Example commit message (this will usually come dynamically)
COMMIT_MESSAGE = "feat: TO3065-17663 crditeng some message"

# API headers with bearer token
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}



COMMIT_MESSAGE = "feat: TO3065-17663 [crditeng] some message"

match = re.search(r"\[(.*?)\]", COMMIT_MESSAGE)
if not match:
    raise Exception(f"Could not parse business unit from commit message: {COMMIT_MESSAGE}")

business_unit = match.group(1).lower()
print(f"✅ Extracted business unit: {business_unit}")


business_unit = match.group(1).lower()
print(f"✅ Extracted business unit: {business_unit}")

# 2️⃣ Get job template ID dynamically by name
search_url = f"{TOWER_HOST}/api/v2/job_templates/?name={JOB_TEMPLATE_NAME}"
resp = requests.get(search_url, headers=HEADERS, verify=False)

if resp.status_code != 200:
    raise Exception(f"Failed to search job template: {resp.status_code} {resp.text}")

results = resp.json().get("results", [])
if not results:
    raise Exception(f"No job template found with name: {JOB_TEMPLATE_NAME}")

job_template_id = results[0]["id"]
print(f"✅ Found job template '{JOB_TEMPLATE_NAME}' with ID {job_template_id}")

# 3️⃣ Get all schedules for this job template
url = f"{TOWER_HOST}/api/v2/job_templates/{job_template_id}/schedules/"
resp = requests.get(url, headers=HEADERS, verify=False)

if resp.status_code != 200:
    raise Exception(f"Failed to fetch schedules: {resp.status_code} {resp.text}")

schedules = resp.json().get("results", [])

if not schedules:
    raise Exception(f"No schedules found for job template {job_template_id}")

print(f"✅ Found {len(schedules)} schedules for job template {job_template_id}")

# 4️⃣ Check if any schedule matches business unit
matched_schedule = None
for sched in schedules:
    if business_unit in sched["name"].replace(" ", "").lower():
        matched_schedule = sched
        break

if not matched_schedule:
    raise Exception(f"No schedule found matching business unit '{business_unit}'")

print(f"✅ Found matching schedule: {matched_schedule['name']} (ID: {matched_schedule['id']})")

# 3️⃣ Get launch parameters from schedule
schedule_id = matched_schedule["id"]
schedule_detail_url = f"{TOWER_HOST}/api/v2/schedules/{schedule_id}/"
resp = requests.get(schedule_detail_url, headers=HEADERS, verify=False)
resp.raise_for_status()

schedule_detail = resp.json()

# Extract launch params (only include if present)
payload = {}
for field in ["extra_data", "inventory", "scm_branch", "job_tags", "limit"]:
    if field in schedule_detail and schedule_detail[field]:
        # Tower expects "extra_data" as "extra_vars" when launching
        if field == "extra_data":
            payload["extra_vars"] = schedule_detail[field]
        else:
            payload[field] = schedule_detail[field]

print(f"📦 Launch payload built: {json.dumps(payload, indent=2)}")

# 4️⃣ Launch the job with these params
launch_url = f"{TOWER_HOST}/api/v2/job_templates/{job_template_id}/launch/"
response = requests.post(launch_url, headers=HEADERS, data=json.dumps(payload), verify=False)

if response.status_code != 201:
    raise Exception(f"Failed to launch job: {response.status_code} {response.text}")

job = response.json()
job_id = job["id"]
print(f"🚀 Job launched! ID: {job_id}")

# 5️⃣ Poll job status
job_url = f"{TOWER_HOST}/api/v2/jobs/{job_id}/"
while True:
    job_resp = requests.get(job_url, headers=HEADERS, verify=False)
    job_resp.raise_for_status()

    job_data = job_resp.json()
    status = job_data["status"]
    print(f"Job {job_id} status: {status}")

    if status in ["successful", "failed", "error", "canceled"]:
        break

    time.sleep(5)

# 6️⃣ Final result
if status == "successful":
    print(f"🎉 Job {job_id} completed successfully")
else:
    print(f"⚠️ Job {job_id} ended with status: {status}")


----

import requests
import json

schedule_id = 123  # matched schedule ID
url = f"{TOWER_HOST}/api/v2/schedules/{schedule_id}/prompt/"

resp = requests.post(url, headers=HEADERS, verify=False)
resp.raise_for_status()

params = resp.json()
print(json.dumps(params, indent=2))

# Build launch payload
payload = {}

if "extra_vars" in params:
    payload["extra_vars"] = params["extra_vars"]
if "inventory" in params:
    payload["inventory"] = params["inventory"]["id"] if isinstance(params["inventory"], dict) else params["inventory"]
if "credentials" in params:
    payload["credentials"] = [c["id"] for c in params["credentials"]]
if "job_tags" in params:
    payload["job_tags"] = params["job_tags"]
if "limit" in params:
    payload["limit"] = params["limit"]
if "scm_branch" in params:
    payload["scm_branch"] = params["scm_branch"]

print("📦 Launch payload ready:", json.dumps(payload, indent=2))

----

# Extra vars
if "extra_data" in schedule_detail and schedule_detail["extra_data"]:
    payload["extra_vars"] = schedule_detail["extra_data"]

# SCM branch
if "scm_branch" in schedule_detail and schedule_detail["scm_branch"]:
    payload["scm_branch"] = schedule_detail["scm_branch"]

# Job tags
if "job_tags" in schedule_detail and schedule_detail["job_tags"]:
    payload["job_tags"] = schedule_detail["job_tags"]

# Limit
if "limit" in schedule_detail and schedule_detail["limit"]:
    payload["limit"] = schedule_detail["limit"]

# Inventory (from summary_fields)
inventory = schedule_detail.get("summary_fields", {}).get("inventory")
if inventory and "id" in inventory:
    payload["inventory"] = inventory["id"]

# 3️⃣ Get credentials from /credentials API
cred_url = f"{TOWER_HOST}/api/v2/schedules/{SCHEDULE_ID}/credentials/"
cred_resp = requests.get(cred_url, headers=HEADERS, verify=False)
cred_resp.raise_for_status()
credentials = cred_resp.json().get("results", [])
if credentials:
    payload["credentials"] = [c["id"] for c in credentials]

print("📦 Launch payload ready:")
print(json.dumps(payload, indent=2))

