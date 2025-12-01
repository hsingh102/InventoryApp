import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

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
    print("EVENT:", json.dumps(event))

    location_id = None

    # 1) From path: /location/{id}
    path_params = event.get("pathParameters") or {}
    if "id" in path_params:
        location_id = path_params["id"]

    # 2) From query string ?location_id=1
    if location_id is None:
        query_params = event.get("queryStringParameters") or {}
        if query_params:
            location_id = query_params.get("location_id")

    # 3) From top-level (for Lambda console tests)
    if location_id is None:
        location_id = event.get("location_id")

    if location_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "location_id is required"})
        }

    # Make sure it's an int (matches DynamoDB attribute type)
    try:
        location_id_int = int(location_id)
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "location_id must be an integer"})
        }

    try:
        # Scan table and filter by location_id
        response = table.scan(
            FilterExpression=Attr("location_id").eq(location_id_int)
        )

        items = _decimal_to_float(response.get("Items", []))

        return {
            "statusCode": 200,
            "body": json.dumps(items)
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }

