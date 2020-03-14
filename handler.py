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

    api_gw = boto3.client('apigatewaymanagementapi',
        endpoint_url=f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}')
    connection_id = event['requestContext']['connectionId']

    try:
        body = json.loads(event['body'])
        output_cb = lambda output: api_gw.post_to_connection(
            Data=str(output).encode('utf8'), ConnectionId=connection_id)
        _run_computer(body['program'], body['input'], output_cb)
    except JSONDecodeError:
        msg = f'Hello connection ID {connection_id}!\n' + \
            'Send JSON object with program and input to run, e.g.\n' + \
            '{"program": [3,0,4,0,99], "input": 42}'
        api_gw.post_to_connection(Data=msg.encode('utf8'), ConnectionId=connection_id)

    response = {
        "statusCode": 200,
        "body": "default"
    }

    return response

def _run_computer(program, inp, output_cb):
    computer = IntcodeComputer(program)
    computer.inputs.append(inp)
    it = computer.run()

    try:
        while True:
            output = next(it)
            output_cb(output)
    except StopIteration:
        pass