import json
from json.decoder import JSONDecodeError

import boto3

from intcode_computer import IntcodeComputer

def connectHandler(event, context):
    print('connectHandler', event)

    response = {
        "statusCode": 200,
        "body": "connect"
    }

    return response

def disconnectHandler(event, context):
    print('disconnectHandler', event)

    response = {
        "statusCode": 200,
        "body": "disconnect"
    }

    return response

def defaultHandler(event, context):
    print('defaultHandler', event)

    gatewayapi = boto3.client('apigatewaymanagementapi',
        endpoint_url=f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}')
    connection_id = event['requestContext']['connectionId']

    try:
        body = json.loads(event['body'])
        msg = _run_computer(body['program'], body['input'])
    except JSONDecodeError:
        msg = f'Hello connection ID {connection_id}!\n' + \
            'Send JSON object with program and input to run, e.g.\n' + \
            '{"program": [3,0,4,0,99], "input": 42}'

    gatewayapi.post_to_connection(Data=msg.encode('utf8'), ConnectionId=connection_id)

    response = {
        "statusCode": 200,
        "body": "default"
    }

    return response

def _run_computer(program, inputs) -> str:
    computer = IntcodeComputer(program)
    computer.inputs.append(inputs)
    it = computer.run()

    last_output = None
    try:
        while True:
            last_output = next(it)
    except StopIteration:
        return str(last_output)