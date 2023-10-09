import json
import traceback
import boto3
import uuid
import time
from flask_lambda import FlaskLambda
from flask import request
from boto3.dynamodb.conditions import Key, Attr

app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
table = ddb.Table('logs')


@app.route('/log', methods=['POST'])
def index():
    try:
        uuid1 = uuid.uuid1()
        uid = str(uuid1.hex)
        timestamp = str(int(time.time() * 1000))
        user_id = request.form.get('userId')
        fail = request.form.get('fail') == 'true'
        status = "Failed" if fail else "Success"
        error_message = "API failed due to some error" if fail else ""
        response = (
            json.dumps({
                "message": "Hello, World!"
            }),
            200,
            {'Content-Type': 'application/json'}
        )

        table.put_item(Item={
            'id': uid,
            'timestamp': timestamp,
            'user_id': user_id,
            'request': request.form,
            'response': {
                "message": "Hello, World!"
            },
            'status': status,
            'error_message': error_message,
        })
        return response
    except Exception as e:
        traceback.print_exc()
        print(e)
        return (
            json.dumps({
                "message": "Something went wrong!"
            }),
            400,
            {'Content-Type': 'application/json'}
        )


@app.route('/logs', methods=['GET'])
def get_logs():
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    items = table.scan(FilterExpression=Key('timestamp').between(from_date, to_date))['Items']
    distinct_users = set([])
    failed_apis = 0
    for item in items:
        distinct_users.add(item.get('user_id'))
        print(distinct_users, 'distinct_users')
        if item.get('status') == 'Failed':
            failed_apis = failed_apis + 1

    data = {
        'items': items,
        'total_count': len(items),
        'distinct_users': len(distinct_users),
        'failed_apis': failed_apis
    }
    return (
        json.dumps(data),
        200,
        {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    )
