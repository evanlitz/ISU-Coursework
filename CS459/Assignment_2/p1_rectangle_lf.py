import json
import traceback

def calculate_area(length, width):
    return length * width

def calculate_perimeter(length, width):
    return 2 * (length + width)

def lambda_handler(event, context):
    try:
        body_raw = event.get("body", None)

        if body_raw is None:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing body"})
            }

        # Function URL gives a JSON string in event["body"]
        body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw

        length = body.get("length", None) if isinstance(body, dict) else None
        width  = body.get("width", None)  if isinstance(body, dict) else None

        if length is None or width is None:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Need length and width"})
            }

        length = float(length)
        width  = float(width)

        area = calculate_area(length, width)
        perimeter = calculate_perimeter(length, width)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"area": area, "perimeter": perimeter})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e), "trace": traceback.format_exc()})
        }
