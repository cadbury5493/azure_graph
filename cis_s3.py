import os
import json
import boto3
import re
from datetime import datetime
from botocore.config import Config

proxies = {
    "https": "http://your.proxy.server:8080"  # Replace if needed
}

def get_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("access_key"),
        aws_secret_access_key=os.getenv("secret_key"),
        region_name=os.getenv("AWS_REGION", "us-west-2"),
        config=Config(proxies=proxies)
    )

def get_all_json_keys(bucket, prefix, s3):
    """Recursively list all JSON files under a prefix."""
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".json"):
                yield key


def process_json_object(s3, bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    data = json.loads(content)

    # Extract platform info safely
    platform_name = data.get("platform", {}).get("name", "")
    platform_release = data.get("platform", {}).get("release", "")
    platform = f"{platform_name} {platform_release}".strip()

    parts = key.split("/")

    ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")
    date = parts[2]
    region = parts[3]
    environment = parts[4]
    instance_file = parts[5]

    base_name = instance_file.rsplit(".json", 1)[0]

    m = re.search(r"-\d{4}-\d{2}-\d{2}-T", base_name)
    if m:
        instance_name = base_name[:m.start()]
    else:
        instance_name = base_name

    host_name = f"Name@{instance_name}"

    output = []

    profiles = data.get("profiles", [])
    for profile in profiles:
        for control in profile.get("controls", []):
            title = control.get("title", "")
            description = control.get("desc", "")
            control_results = control.get("results", [])

            # 🔹 Determine overall control status
            overall_status = "passed"
            for r in control_results:
                if r.get("status", "").lower() == "failed":
                    overall_status = "failed"
                    break

            output.append({
                "host_name": host_name,
                "title": title,
                "description": description,
                "status": overall_status,
                "code_desc": None,  # optional, since we are keeping full results
                "platform": platform,
                "environment": environment,
                "region": region,
                "ingestion_date": ingestion_date,
                "results": control_results,  # ✅ keep original results array
                "bunit": "crdpm"
            })

    return output



def main():
    s3 = get_client()

    bucket = "prod-db-backup-daily"
    prefix = "CIS-Scans/weekly-reports/2026-02-10/"

    final_output = []

    print("Scanning S3 path...")
    for key in get_all_json_keys(bucket, prefix, s3):
        print(f"Processing: {key}")
        records = process_json_object(s3, bucket, key)
        final_output.extend(records)

    with open("aggregated_output.json", "w") as f:
        json.dump(final_output, f, indent=2)

    print(f"\n✅ Done. Total flattened records: {len(final_output)}")


if __name__ == "__main__":
    main()
