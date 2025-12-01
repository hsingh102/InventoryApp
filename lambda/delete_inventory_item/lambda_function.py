import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # ================
    # 1. Get item_id from path /item/{id}
    # ================
    path_params = event.get("pathParameters") or {}
    item_id = path_params.get("id")

    # ================
    # 2. Get location_id from body or queryString
    # ================
    location_id = None

    # Body (API proxy sends string)
    body_str = event.get("body")
    if body_str:
        try:
            body = json.loads(body_str)
            location_id = body.get("location_id")
        except Exception:
            pass

    # Query string fallback
    if location_id is None:
        qs = event.get("queryStringParameters") or {}
        location_id = qs.get("location_id")

    # Lambda console test fallback
    if location_id is None:
        location_id = event.get("location_id")

    # ================
    # Validation
    # ================
    if not item_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "item_id is required"})
        }

    if location_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "location_id is required"})
        }

    try:
        location_id = int(location_id)
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "location_id must be an integer"})
        }

    # ================
    # 3. Perform delete
    # ================
    try:
        table.delete_item(
            Key={
                "item_id": item_id,
                "location_id": location_id
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Item deleted", "item_id": item_id})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
