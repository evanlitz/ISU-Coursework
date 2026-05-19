import json
import boto3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    resp = s3.list_buckets()
    buckets = resp.get("Buckets", [])

    count = len(buckets)

    if count == 0:
        out = {"bucket_count": "none"}
    else:
        out = {"bucket_count": count}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(out)
    }
