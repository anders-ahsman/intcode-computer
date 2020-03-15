import json
from json.decoder import JSONDecodeError

import boto3

from intcode_computer import IntcodeComputer, IntcodeProgramException

def connect_handler(event, context):
    print('connect_handler', event)

    response = {
        "statusCode": 200,
        "body": "connect"
    }

    return response

def disconnect_handler(event, context):
    print('disconnect_handler', event)

    response = {
        "statusCode": 200,
        "body": "disconnect"
    }

    return response

def default_handler(event, context):
    print('default_handler', event)

    api_gw = boto3.client('apigatewaymanagementapi',
        endpoint_url=f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}')
    connection_id = event['requestContext']['connectionId']

    def send_to_client(msg: str) -> None:
        api_gw.post_to_connection(Data=msg.encode('utf8'), ConnectionId=connection_id)

    try:
        body = json.loads(event['body'])
        _run_program(body['program'], body['input'], lambda output: send_to_client(str(output)))
        send_to_client('Program completed.')
    except (JSONDecodeError, KeyError):
        msg = f'Hello connection ID {connection_id}!\n' + \
            'Send JSON object with program and input to run, e.g.\n' + \
            '{"program": [3,0,4,0,99], "input": 42}'
        send_to_client(msg)
    except IntcodeProgramException as e:
        send_to_client(f'Intcode program error: {e}')

    response = {
        "statusCode": 200,
        "body": "default"
    }

    return response

def _run_program(program, inp, output_cb):
    computer = IntcodeComputer(program)
    computer.inputs.append(inp)
    it = computer.run()

    try:
        while True:
            output = next(it)
            output_cb(output)
    except StopIteration:
        pass