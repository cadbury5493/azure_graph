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
