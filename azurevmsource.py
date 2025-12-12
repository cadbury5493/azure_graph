import re

def detect_detailed_os(vm):
    """Extracts detailed OS info from image_reference, including custom gallery images."""
    if (not vm.storage_profile) or (not vm.storage_profile.image_reference):
        return "unknown", "unknown"

    img = vm.storage_profile.image_reference

    # First: try normal publisher/offer/sku logic
    publisher = (getattr(img, "publisher", "") or "").lower()
    offer = (getattr(img, "offer", "") or "").lower()
    sku = (getattr(img, "sku", "") or "").lower()

    # Standard marketplace logic (optional)
    if offer or sku:
        if "windows" in offer:
            return f"windows {sku.replace('-', ' ')}", sku
        if "redhat" in publisher or "rhel" in offer:
            return f"rhel {sku}", sku
        if "ubuntu" in offer:
            normalized = sku.replace("_", ".").replace("-", " ")
            return f"ubuntu {normalized}", sku
        if "suse" in offer or "sles" in offer:
            return f"suse {sku}".replace("-", " "), sku
        if "oracle" in publisher or "ol" in offer:
            return f"oracle {sku}", sku
        if "debian" in offer:
            return f"debian {sku}", sku

    # --------------------------
    # CUSTOM GALLERY IMAGE LOGIC
    # --------------------------
    img_id = getattr(img, "id", "") or ""

    # Extract OS name (part after ".../images/<os_name>/")
    os_match = re.search(r"/images/([^/]+)/Versions/", img_id, re.IGNORECASE)
    os_name = os_match.group(1) if os_match else "unknown"

    # Extract version (part after ".../Versions/<version>")
    ver_match = re.search(r"/Versions/([^/]+)$", img_id, re.IGNORECASE)
    os_version = ver_match.group(1) if ver_match else "unknown"

    return os_name, os_version

----
creation_dt = getattr(vm, "time_created", None)
creation_date = creation_dt.isoformat() if creation_dt else None

from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest
import json
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
TENANT_ID = "<your-tenant-id>"
CLIENT_ID = "<your-client-id>"
CLIENT_SECRET = "<your-client-secret>"

BUNIT = "ssc_azure"
EXEC_MODE = "weekly_azure_vm_count"
INGESTION_DATE = datetime.utcnow().strftime("%Y-%m-%d")

# -------------------------------
# AUTHENTICATION
# -------------------------------
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

subscription_client = SubscriptionClient(credential)
resource_graph_client = ResourceGraphClient(credential)

# -------------------------------
# FETCH VM CREATION DATES FROM RESOURCE GRAPH
# -------------------------------
creation_query = QueryRequest(
    subscriptions=[s.subscription_id for s in subscription_client.subscriptions.list()],
    query="""
        Resources
        | where type =~ 'Microsoft.Compute/virtualMachines'
        | project id, name, subscriptionId, timeCreated = properties.timeCreated
    """
)

creation_results = resource_graph_client.resources(creation_query)

# Store creation dates in a dictionary for lookup
creation_map = {
    item["id"]: item.get("timeCreated")
    for item in creation_results.data
}

# -------------------------------
# MAIN INVENTORY LOGIC
# -------------------------------
vm_inventory = []
total_vm_count = 0

for sub in subscription_client.subscriptions.list():
    subscription_id = sub.subscription_id
    compute_client = ComputeManagementClient(credential, subscription_id)

    print(f"Fetching VMs for subscription: {subscription_id}")

    try:
        vms = compute_client.virtual_machines.list_all()
    except Exception as e:
        print(f"Error fetching VMs for subscription {subscription_id}: {e}")
        continue

    for vm in vms:
        total_vm_count += 1

        vm_id = vm.id
        host_name = vm.name
        region = vm.location
        environment = vm.tags.get("environment") if vm.tags else "unknown"

        # Determine OS platform
        platform = "unknown"
        if vm.storage_profile and vm.storage_profile.os_disk:
            if vm.storage_profile.os_disk.os_type:
                platform = str(vm.storage_profile.os_disk.os_type).lower()

        # Fetch power state
        instance_view = compute_client.virtual_machines.instance_view(
            vm.resource_group_name, vm.name
        )
        statuses = instance_view.statuses
        status = "unknown"
        for s in statuses:
            if s.code.startswith("PowerState/"):
                status = s.code.split("/")[-1]

        # Lookup creation date
        creation_date = creation_map.get(vm_id)

        record = {
            "bunit": BUNIT,
            "subscription": subscription_id,
            "host_name": host_name,
            "region": region,
            "environment": environment,
            "platform": platform,
            "status": status,
            "creation_date": creation_date,
            "exec_mode": EXEC_MODE,
            "ingestion_date": INGESTION_DATE
        }

        vm_inventory.append(record)

# -------------------------------
# OUTPUT
# -------------------------------
print(f"\nTotal VMs fetched: {total_vm_count}")
print("\nFinal JSON Output:")
print(json.dumps(vm_inventory, indent=4))
