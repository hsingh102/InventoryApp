import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')


def lambda_handler(event, context):
    # Log event for debugging
    print("EVENT:", json.dumps(event))

    # ---------- 1. Read body safely ----------
    body = {}

    body_str = event.get("body")
    if isinstance(body_str, str):
        # Normal case: API Gateway proxy sends JSON string in "body"
        try:
            body = json.loads(body_str)
        except Exception:
            body = {}
    elif isinstance(body_str, dict):
        # Just in case body is already a dict
        body = body_str

    # ---------- 2. Read fields (body first, then top-level for Lambda tests) ----------
    item_id = body.get("item_id") or event.get("item_id")
    location_id = body.get("location_id") if body.get("location_id") is not None else event.get("location_id")
    item_name = body.get("item_name") or event.get("item_name")
    item_description = body.get("item_description") or event.get("item_description")
    qty_on_hand = body.get("qty_on_hand") if body.get("qty_on_hand") is not None else event.get("qty_on_hand")
    price = body.get("price") if body.get("price") is not None else event.get("price")

    # ---------- 3. Basic validation ----------
    if not item_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "item_id is required"})
        }

    if location_id is None or item_name is None or qty_on_hand is None or price is None:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "location_id, item_name, qty_on_hand and price are required"
            })
        }

    # ---------- 4. Save item to DynamoDB ----------
    try:
        # Convert numeric fields
        location_id = int(location_id)
        qty_on_hand = int(qty_on_hand)
        price = Decimal(str(price))

        table.put_item(
            Item={
                "item_id": item_id,
                "location_id": location_id,
                "item_name": item_name,
                "item_description": item_description or "",
                "item_qty_on_hand": qty_on_hand,
                "item_price": price
            }
        )

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "Item created", "item_id": item_id})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }


