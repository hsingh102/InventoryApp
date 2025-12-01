import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')

def _decimal_to_float(obj):
    if isinstance(obj, list):
        return [_decimal_to_float(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def lambda_handler(event, context):
    # Log event for debugging
    print("EVENT:", json.dumps(event))

    item_id = None
    location_id = None

    # 1) From API Gateway path parameter /item/{id}
    path_params = event.get("pathParameters") or {}
    item_id = path_params.get("id")

    # 2) From API Gateway query string ?location_id=1
    query_params = event.get("queryStringParameters") or {}
    if query_params:
        location_id = query_params.get("location_id")

    # 3) From JSON body (if someone sends it there)
    if (not item_id or not location_id) and event.get("body"):
        try:
            body = json.loads(event["body"])
            item_id = item_id or body.get("item_id")
            location_id = location_id or body.get("location_id")
        except Exception:
            pass

    # 4) From top-level keys (your simple Lambda console test)
    if not item_id:
        item_id = event.get("item_id")
    if not location_id:
        location_id = event.get("location_id")

    # Validate
    if not item_id or location_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "item_id and location_id are required"})
        }

    try:
        response = table.get_item(
            Key={
                "item_id": item_id,
                "location_id": int(location_id)
            }
        )

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Item not found"})
            }

        item = _decimal_to_float(response["Item"])

        return {
            "statusCode": 200,
            "body": json.dumps(item)
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
