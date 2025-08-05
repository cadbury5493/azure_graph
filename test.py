# Place this code within your existing file, replacing the main data loop and adding new functions as needed

def get_vm_ids(token, subscription_id, baseline):
    """Fetch VM IDs for a given subscription and baseline."""
    url = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    query = f"""
    guestconfigurationresources
    | where subscriptionId == '{subscription_id}'
    | where type =~ 'microsoft.guestconfiguration/guestconfigurationassignments'
    | where name contains '{baseline}'
    | project id, vmid = split(properties.targetResourceId, '/')[(-1)]
    | order by id
    """

    body = {
        "subscriptions": [subscription_id],
        "query": query,
        "options": {"resultFormat": "objectArray"}
    }

    response = with_retries(lambda: requests.post(url, headers=headers, json=body, proxies=PROXIES, verify=VERIFY_SSL))
    return response.json().get("data", [])


def query_vm_compliance(token, subscription_id, vm_id, baseline):
    """Fetch compliance data for a specific VM ID."""
    url = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    query_template = WINDOWS_QUERY if "windows" in baseline.lower() else LINUX_QUERY
    query = query_template.replace(
        "| where subscriptionId == '{subscription_id}'", f"| where id == '{vm_id}'"
    ).replace("{subscription_id}", subscription_id).replace("{baseline}", baseline)

    body = {
        "subscriptions": [subscription_id],
        "query": query,
        "options": {"resultFormat": "objectArray"}
    }

    response = with_retries(lambda: requests.post(url, headers=headers, json=body, proxies=PROXIES, verify=VERIFY_SSL))
    return response.json().get("data", [])


# Replace the section in your main loop starting from:
# for baseline in BASELINES:
# To the following:

for baseline in BASELINES:
    log(f"\n--- Processing Baseline: {baseline} ---", BLUE)
    filename = f"{baseline}_REST_{env_label}_{current_date}"
    csv_filepath = os.path.join(source_dir, f"{filename}.csv")
    json_filepath = os.path.join(source_dir, f"{filename}.json")

    headers = ["bunit", "subscription", "report_id", "date", "host_name", "region",
               "environment", "platform", "status", "cis_id", "id", "message", "exec_mode"]

    all_rows = []
    unique_vm_set = set()
    vm_control_info = defaultdict(lambda: defaultdict(list))

    log(f"Starting to collect data for baseline [{baseline}] across {len(subscriptions)} subscriptions...", CYAN)

    for sub_id, sub_name in subscriptions:
        vms = get_vm_ids(token, sub_id, baseline)
        log(f"{sub_name}: Found {len(vms)} VM(s) to scan", MAGENTA)

        for vm in vms:
            vm_id = vm["id"]
            vm_name = vm["vmid"]
            log(f"Querying VM: {vm_name}", CYAN)

            try:
                results = query_vm_compliance(token, sub_id, vm_id, baseline)
                for r in results:
                    r["message"] = filter_message(r.get("message", ""))
                    if r["message"] == "":
                        continue

                    r["exec_mode"] = exec_mode

                    unique_vm_set.add(r["host_name"])
                    vm_control_info[sub_name][r["host_name"]].append(r)
                    all_rows.append(r)
            except Exception as e:
                log(f"Error querying VM {vm_name}: {e}", RED)
                continue

    log(f"\nTotal unique VMs for baseline [{baseline}]: {len(unique_vm_set)}", CYAN)
    log(f"Total rows for baseline [{baseline}]: {len(all_rows)}", CYAN)

    if not all_rows:
        log(f"No compliance data found for baseline: {baseline}", RED)
        continue

    total_duplicate_vm_count = 0
    for sub_name, vms in vm_control_info.items():
        log(f"{baseline} - {sub_name}", MAGENTA)
        for vm, controls in vms.items():
            log(f"    ({vm}) : {len(controls)} controls", CYAN)

            cis_id_counts = defaultdict(int)
            for control in controls:
                cis_id = control.get("cis_id")
                if cis_id:
                    cis_id_counts[cis_id] += 1

            duplicates = [cid for cid, count in cis_id_counts.items() if count > 1]

            if duplicates:
                total_duplicate_vm_count += 1
                log(f"        {len(duplicates)} duplicated cis_id(s) found!", YELLOW)
                for d in duplicates:
                    log(f"            - Duplicated cis_id: {d} (count: {cis_id_counts[d]})", RED)

    log(f"\nWriting CSV to: {csv_filepath}", GREEN)
    with open(csv_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in all_rows:
            filtered_row = {key: row.get(key, "") for key in headers}
            writer.writerow(filtered_row)

    log(f"Writing JSON to: {json_filepath}", GREEN)
    with open(json_filepath, mode="w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    log(f"\nDone writing for baseline: {baseline}", GREEN)
