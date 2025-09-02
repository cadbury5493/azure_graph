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

# 5️⃣ Extract launch parameters from schedule
extra_vars = matched_schedule.get("extra_data", {})
inventory_id = matched_schedule.get("inventory")
scm_branch = matched_schedule.get("scm_branch")
job_tags = matched_schedule.get("job_tags")

payload = {
    "extra_vars": extra_vars
}
if inventory_id:
    payload["inventory"] = inventory_id
if scm_branch:
    payload["scm_branch"] = scm_branch
if job_tags:
    payload["job_tags"] = job_tags

print(f"📦 Launch payload prepared: {json.dumps(payload, indent=2)}")

# 6️⃣ Get underlying job template ID from schedule
unified_job_template = matched_schedule["unified_job_template"]
job_template_id = unified_job_template.split("/")[-2]  # extract ID
print(f"✅ Schedule is tied to job template ID: {job_template_id}")

# 7️⃣ Launch the job template with schedule's parameters
launch_url = f"{TOWER_HOST}/api/v2/job_templates/{job_template_id}/launch/"
response = requests.post(launch_url, headers=HEADERS, data=json.dumps(payload), verify=False)

if response.status_code != 201:
    raise Exception(f"Failed to launch job: {response.status_code} {response.text}")

job = response.json()
job_id = job["id"]
print(f"🚀 Job launched from schedule! Job ID: {job_id}")

# 8️⃣ Poll job status
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

# 9️⃣ Final result
if status == "successful":
    print(f"🎉 Job {job_id} completed successfully")
else:
    print(f"⚠️ Job {job_id} ended with status: {status}")

