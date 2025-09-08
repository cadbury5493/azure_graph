import re
import yaml

# Example commit messages
COMMIT_MESSAGE_1 = "feat: TO3065-17663 [azure] some message"
COMMIT_MESSAGE_2 = "feat: TO3065-17663 [azure,gl,ssgx] some message"

# Load YAML
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def extract_business_units(commit_msg: str):
    """
    Extract business units inside [] from commit message
    Example: [azure,gl,ssgx] -> ["azure", "gl", "ssgx"]
    """
    match = re.search(r"\[(.*?)\]", commit_msg)
    if not match:
        return []
    return [bu.strip() for bu in match.group(1).split(",")]

def get_jobs_for_business_units(business_units, config):
    """
    Fetch jobs for the selected business units from config.yaml
    """
    jobs = {}
    for bu in business_units:
        if bu not in config:
            continue
        jobs[bu] = config[bu]
    return jobs

# Example usage
bus = extract_business_units(COMMIT_MESSAGE_2)
print("Business Units found:", bus)

jobs = get_jobs_for_business_units(bus, config)
print("Jobs to execute:", jobs)

# Iterate and trigger ansible jobs (pseudo code)
for bu, sections in jobs.items():
    for system, job_list in sections.items():
        for job in job_list:
            schedule = job["schedule_name"]
            inventory = job["inventory"]
            template = job["job_template"]
            tags = job["job_tags"]

            # Example ansible call (replace with actual subprocess/run)
            print(f"Running {template} on {inventory} with tags={tags}, schedule={schedule}")
