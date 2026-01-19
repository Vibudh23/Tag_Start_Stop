import os
import boto3

ec2 = boto3.client("ec2")

TAG_KEY = os.environ.get("TAG_KEY", "RunSchedule")
TAG_VALUE = os.environ.get("TAG_VALUE", "OfficeHours-IST-8to5-MonFri")

def get_instance_ids_by_tag():
    filters = [
        {"Name": f"tag:{TAG_KEY}", "Values": [TAG_VALUE]},
        {"Name": "instance-state-name", "Values": ["running", "stopped"]}
    ]
    paginator = ec2.get_paginator("describe_instances")

    ids = []
    for page in paginator.paginate(Filters=filters):
        for res in page.get("Reservations", []):
            for inst in res.get("Instances", []):
                ids.append(inst["InstanceId"])
    return ids

def lambda_handler(event, context):
    action = (event.get("action") or "").lower().strip()
    if action not in ("start", "stop"):
        raise ValueError("Missing/invalid action. Use: start|stop")

    instance_ids = get_instance_ids_by_tag()

    # IMPORTANT: Always return instanceIds key (even if empty)
    if not instance_ids:
        return {
            "status": "ok",
            "message": "No instances matched tag",
            "tag": f"{TAG_KEY}={TAG_VALUE}",
            "instanceIds": []
        }

    if action == "start":
        ec2.start_instances(InstanceIds=instance_ids)
    else:
        ec2.stop_instances(InstanceIds=instance_ids)

    return {
        "status": "ok",
        "action": action,
        "count": len(instance_ids),
        "tag": f"{TAG_KEY}={TAG_VALUE}",
        "instanceIds": instance_ids
    }
