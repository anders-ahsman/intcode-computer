import datetime
import json
from json.decoder import JSONDecodeError
import os
from typing import Callable

import boto3

from intcode_computer import (
    IntcodeComputer, IntcodeProgramException, MissingInputException)


INTCODE_TABLE = os.getenv('INTCODE_TABLE')
MISSING_INPUT_MSG = \
    'Additional input required. Send using JSON object, e.g.\n' + \
    '{"action": "additional_input", "input": [5]}'
PROGRAM_COMPLETED_MSG = \
    'Program already completed.\n' + \
    'Send new program to run, e.g.\n' + \
    '{"action": "run", "program": [3,0,4,0,99], "input": [42]}'
USAGE_MSG = \
    'Send JSON object with program and input to run, e.g.\n' + \
    '{"action": "run", "program": [4,2,99], "input": []}'
RESPONSE = {'statusCode': 200, 'body': ''}

def connect_handler(event, context):
    print('event:', event)

    return RESPONSE

def disconnect_handler(event, context):
    print('event:', event)

    return RESPONSE

def default_handler(event, context):
    print('event:', event)

    api_gw = boto3.client('apigatewaymanagementapi',
        endpoint_url=f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}')
    connection_id = event['requestContext']['connectionId']

    def send_to_client(msg: str) -> None:
        api_gw.post_to_connection(Data=msg.encode('utf8'), ConnectionId=connection_id)

    try:
        body = json.loads(event['body'])
        computer = IntcodeComputer(body['program'], body['input'])
        try:
            _run_program(computer, lambda output: send_to_client(str(output)))
            send_to_client('Program completed.')
        except MissingInputException:
            _save_state(computer, connection_id)
            send_to_client(MISSING_INPUT_MSG)
        except IntcodeProgramException as e:
            send_to_client(f'Intcode program error: {e}')
    except (JSONDecodeError, KeyError):
        send_to_client(USAGE_MSG)

    return RESPONSE

def additional_input_handler(event, context):
    print('event:', event)

    api_gw = boto3.client('apigatewaymanagementapi',
        endpoint_url=f'https://{event["requestContext"]["domainName"]}/{event["requestContext"]["stage"]}')
    connection_id = event['requestContext']['connectionId']

    def send_to_client(msg: str) -> None:
        api_gw.post_to_connection(Data=msg.encode('utf8'), ConnectionId=connection_id)

    try:
        computer = _load_state(connection_id)
        if computer.has_completed:
            send_to_client(PROGRAM_COMPLETED_MSG)
            return RESPONSE

        try:
            body = json.loads(event['body'])
            for inp in body['input']:
                computer.inputs.append(inp)
            _run_program(computer, lambda output: send_to_client(str(output)))
            _save_state(computer, connection_id)
            send_to_client('Program completed.')
        except MissingInputException:
            send_to_client(MISSING_INPUT_MSG)
            _save_state(computer, connection_id)
        except IntcodeProgramException as e:
            send_to_client(f'Intcode program error: {e}')
        except (JSONDecodeError, KeyError):
            send_to_client(USAGE_MSG)
    except KeyError:
        send_to_client(USAGE_MSG)

    return RESPONSE

def _run_program(computer: IntcodeComputer, output_cb: Callable[[int], None]):
    it = computer.run()

    try:
        while True:
            output = next(it)
            output_cb(output)
    except StopIteration:
        pass

def _save_state(computer: IntcodeComputer, connection_id: str) -> None:
    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(
        TableName=INTCODE_TABLE,
        Item={
            'ConnectionId': {'S': connection_id},
            'LastUpdate': {'S': datetime.datetime.utcnow().astimezone().isoformat()},
            'State': {'S': computer.serialize_state()}
        })

def _load_state(connection_id: int) -> IntcodeComputer:
    dynamodb = boto3.client('dynamodb')
    response = dynamodb.get_item(
        TableName=INTCODE_TABLE,
        Key={
            'ConnectionId': {'S': connection_id}
        })
    state = response['Item']['State']['S']
    computer = IntcodeComputer([], [])
    computer.load_serialized_state(state)
    return computer
