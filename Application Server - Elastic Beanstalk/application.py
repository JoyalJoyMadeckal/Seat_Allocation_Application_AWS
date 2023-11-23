from flask import Flask, render_template, request, session, jsonify
import boto3
import random

app = application = Flask(__name__)
app.secret_key = "abcd"

@app.route('/')
def index():
    return jsonify({})

@app.route('/fetchseatsallocated')
def fetchseatsallocated():
    client = boto3.resource("dynamodb", region_name='us-east-1')
    table = client.Table('Seat_allocated')
    resp = table.scan()
    allocated_seats = [seat['Seat_no'] for seat in resp['Items']]
    users_with_seats = list(set([user['User ID'] for user in resp['Items']]))
    return {'users': users_with_seats,'allocated_seats':allocated_seats}


@app.route('/login/validate', methods=['GET', 'POST'])
def validate_login():
    input = request.get_json(force=True)
    client = boto3.client("dynamodb", region_name='us-east-1')
    userObj = client.get_item(
        TableName = 'Users',
        Key = {'User ID' : {'S':input["user_name"]}}
    )

    if 'Item' in userObj.keys():
        if input['password'] == userObj['Item']['Passcode']['S']:
            admin = False
            if userObj['Item']['Role']['S'] == 'Admin':
                admin = True
            return {'validate': True, 'admin': admin}
    return {'validate': False}

@app.route('/updateseatallocation', methods=['POST'])
def updateseatallocation():
    input = request.get_json(force=True)

    if set(input['new_seats']) == set(input['old_seats']):
        return {}

    client = boto3.client("dynamodb", region_name='us-east-1')

    put_request_objects = [{'PutRequest': {'Item' : {'User ID': {'S': f'Blocked {random.randint(0,10000)}'}, 'Seat_no':{'S': seat}}}} for seat in input['new_seats']]
    del_request_objects = [{'DeleteRequest':{'Key':{'User ID': {'S': user}}}} for user in input['users']]

    put_request_objects.extend(del_request_objects)

    client.batch_write_item(
        RequestItems = {
            'Seat_allocated': put_request_objects
        }
    )
    return {'response': 200}
