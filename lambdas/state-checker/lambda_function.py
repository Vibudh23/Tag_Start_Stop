import boto3

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    instance_ids = event.get("instanceIds", [])
    desired = event.get("desiredState")

    if not instance_ids:
        return {
            "allOk": True,
            "states": {},
            "note": "No instanceIds provided"
        }

    if desired not in ["running", "stopped"]:
        return {
            "allOk": False,
            "states": {},
            "error": "desiredState must be running or stopped"
        }

    resp = ec2.describe_instances(InstanceIds=instance_ids)

    states = {}
    for reservation in resp.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            states[instance["InstanceId"]] = instance["State"]["Name"]

    # If any missing instances from describe => not ok
    if len(states) != len(instance_ids):
        return {
            "allOk": False,
            "states": states,
            "missingCount": len(instance_ids) - len(states)
        }

    all_ok = all(state == desired for state in states.values())

    return {
        "allOk": all_ok,
        "states": states,
        "desiredState": desired
    }

