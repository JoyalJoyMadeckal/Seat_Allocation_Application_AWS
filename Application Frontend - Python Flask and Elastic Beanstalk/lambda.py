import boto3

def lambda_handler(event, context):
    
    client = boto3.client("dynamodb", region_name='us-east-1')
    
    client.put_item(
            TableName = 'Seat_allocated',
            Item = {
                'User ID': {'S': event['user']},
                'Seat_no': {'S': event['seat']}
            }
        )
    
    
    return {"response": 200}
