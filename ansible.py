import requests
import json
import time

# Tower/AWX details
TOWER_HOST = "https://your-tower-host"
USERNAME = "your-username"
PASSWORD = "your-password"

# Job template ID in Ansible Tower
JOB_TEMPLATE_ID = 42  

# Launch endpoint
launch_url = f"{TOWER_HOST}/api/v2/job_templates/{JOB_TEMPLATE_ID}/launch/"

# Custom parameters (extra_vars)
extra_vars = {
    "package_name": "nginx",
    "state": "latest",
    "environment": "dev"
}

# Launch the job
response = requests.post(
    launch_url,
    auth=(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"},
    data=json.dumps({"extra_vars": extra_vars}),
    verify=False  # set True if cert is valid
)

if response.status_code != 201:
    raise Exception(f"Failed to launch job: {response.status_code} {response.text}")

job = response.json()
job_id = job["id"]
print(f"✅ Job launched! ID: {job_id}")

# Poll job status
job_url = f"{TOWER_HOST}/api/v2/jobs/{job_id}/"

while True:
    job_resp = requests.get(job_url, auth=(USERNAME, PASSWORD), verify=False)
    if job_resp.status_code != 200:
        raise Exception(f"Failed to get job status: {job_resp.status_code} {job_resp.text}")

    job_data = job_resp.json()
    status = job_data["status"]
    print(f"Job {job_id} status: {status}")

    if status in ["successful", "failed", "error", "canceled"]:
        break

    time.sleep(5)  # wait before next poll

# Final result
if status == "successful":
    print(f"🎉 Job {job_id} completed successfully")
else:
    print(f"⚠️ Job {job_id} ended with status: {status}")

-----
import requests
import json
import time

# Tower/AWX details
TOWER_HOST = "https://your-tower-host"
BEARER_TOKEN = "your-api-token"

# Job template name (human-readable, as in Tower UI)
JOB_TEMPLATE_NAME = "Install Nginx"

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

# 2️⃣ Launch the job
launch_url = f"{TOWER_HOST}/api/v2/job_templates/{job_template_id}/launch/"

extra_vars = {
    "package_name": "nginx",
    "state": "latest",
    "environment": "dev"
}

response = requests.post(
    launch_url,
    headers=HEADERS,
    data=json.dumps({"extra_vars": extra_vars}),
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
    print(f"🎉 Job {job_id} completed successfully")
else:
    print(f"⚠️ Job {job_id} ended with status: {status}")

----

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
    print(f"🎉 Job {job_id} completed successfully")
else:
    print(f"⚠️ Job {job_id} ended with status: {status}")
