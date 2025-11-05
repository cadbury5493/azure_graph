import boto3
import json
import os
from datetime import datetime
from urllib.parse import urlparse
from botocore.config import Config

# ✅ Define your proxy once here
proxies = {
    "https": "http://your.proxy.server:8080"   # <-- replace with your actual proxy if needed
}


def get_client():
    """Create an S3 client using environment variables and a constant proxy configuration."""
    aws_access_key_id = os.getenv("access_key")
    aws_secret_access_key = os.getenv("secret_key")
    region = os.getenv("AWS_REGION", "us-west-2")

    boto_config = Config(proxies=proxies)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
        config=boto_config
    )

    return s3_client


def get_s3_objects(bucket, prefix, s3):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                yield obj["Key"]


def process_json_object(s3, bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    data = json.loads(content)

    # Extract platform info safely
    platform_name = data.get("platform", {}).get("name", "")
    platform_release = data.get("platform", {}).get("release", "")
    platform = f"{platform_name} {platform_release}".strip()

    # Parse S3 key for metadata
    parts = key.split("/")
    # Example: ['DM018', 'weekly-reports', '2025-11-05', 'us-west-2', 'prod', 'i-xxxx.json']
    ingestion_date = datetime.utcnow().strftime("%Y-%m-%d")
    date = parts[2]
    region = parts[3]
    environment = parts[4]
    instance_file = parts[5]
    base_name = instance_file.replace(".json", "")
    instance_name = re.sub(r"-\d{4}-\d{2}-\d{2}-T\d{2}-\d{2}-\d{2}Z$", "", base_name)

    host_name = f"Name@{instance_name}"

    results = []
    profiles = data.get("profiles", [])
    for profile in profiles:
        for control in profile.get("controls", []):
            title = control.get("title", "")
            description = control.get("desc", "")
            for result in control.get("results", []):
                status = result.get("status", "")
                code_desc = result.get("code_desc", "")
                results.append({
                    "host_name": host_name,
                    "title": title,
                    "description": description,
                    "status": status,
                    "code_desc": code_desc,
                    "platform": platform,
                    "environment": environment,
                    "region": region,
                    "ingestion_date": ingestion_date,
                    "bunit": "crdpm"
                })
    return results


def main():
    s3 = get_client()
    s3_path = "s3://prod-db-backup-daily/DM018/weekly-reports/"
    parsed = urlparse(s3_path)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip("/")

    final_output = []
    for key in get_s3_objects(bucket, prefix, s3):
        print(f"Processing: {key}")
        records = process_json_object(s3, bucket, key)
        final_output.extend(records)

    # Save final JSON locally
    with open("aggregated_output.json", "w") as f:
        json.dump(final_output, f, indent=2)

    print(f"\n✅ Aggregation complete. Total records: {len(final_output)}")
    print("Output written to aggregated_output.json")


if __name__ == "__main__":
    main()
