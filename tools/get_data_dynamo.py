import boto3

# Set the AWS CLI profile name
aws_profile = 'generic-dev'
table_name = 'generico2022-db'
filter_expression = 'entity = :val'
expression_attribute_values = {':val': {'S': 'articulos'}}
page_size = 250
session = boto3.Session(profile_name=aws_profile)

dynamodb = session.client('dynamodb')

def scan_page(table_name, filter_expression, expression_attribute_values, limit, exclusive_start_key=None):
    params = {
        'TableName': table_name,
        'FilterExpression': filter_expression,
        'ExpressionAttributeValues': expression_attribute_values,
        'Limit': limit
    }
    if exclusive_start_key is not None:
        params['ExclusiveStartKey'] = exclusive_start_key

    response = dynamodb.scan(**params)
    items = response['Items']
    last_evaluated_key = response.get('LastEvaluatedKey')
    return items, last_evaluated_key

scanned_items = []
last_evaluated_key = None

while True:
    page_items, last_evaluated_key = scan_page(
        table_name,
        filter_expression,
        expression_attribute_values,
        page_size,
        last_evaluated_key
    )

    scanned_items.extend(page_items)

    if last_evaluated_key is None:
        break

with open("dynamo.txt", "w") as f:
    for item in scanned_items:
        boto3.resource('dynamodb', region_name="us-east-2")
        deserializer = boto3.dynamodb.types.TypeDeserializer()
        data = {k: deserializer.deserialize(v) for k,v in item.items()}
        print(data["art_des"])
        f.write(data["co_art"] + "\t" + data["art_des"].strip() + "\n")
