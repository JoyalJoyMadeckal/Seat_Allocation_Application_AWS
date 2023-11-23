import boto3

client = boto3.client("dynamodb", region_name='us-east-1')

print(client.list_tables())

# dynamodb = boto3.resource("dynamodb", region_name='us-east-1')

table = client.create_table(
    TableName='users',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'last_name',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'last_name',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

waiter = client.get_waiter('table_exists')

waiter.wait(
    TableName='users'
)

# Wait until the table exists.
# table.wait_until_exists()

# Print out some data about the table.
print(table)

# print(client.list_tables())
