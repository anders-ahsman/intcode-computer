import json
from unittest.mock import patch, Mock

from handler import defaultHandler

event = {
	'requestContext': {
		'routeKey': '$default',
		'messageId': 'JZAn6em3Ai0AbBg=',
		'eventType': 'MESSAGE',
		'extendedRequestId': 'JZAn6GiNgi0FSgA=',
		'requestTime': '14/Mar/2020:17:30:00 +0000',
		'messageDirection': 'IN',
		'stage': 'dev',
		'connectedAt': 1584206948743,
		'requestTimeEpoch': 1584207000957,
		'identity': {
			'cognitoIdentityPoolId': None,
			'cognitoIdentityId': None,
			'principalOrgId': None,
			'cognitoAuthenticationType': None,
			'userArn': None,
			'userAgent': None,
			'accountId': None,
			'caller': None,
			'sourceIp': '1.2.3.4',
			'accessKey': None,
			'cognitoAuthenticationProvider': None,
			'user': None
		},
		'requestId': 'JZAn6GiNgi0FSgA=',
		'domainName': '18nqx05mb2.execute-api.eu-north-1.amazonaws.com',
		'connectionId': 'JZAfwei5Ai0AbBg=',
		'apiId': '18nqx05mb2'
	},
	'body': None,
	'isBase64Encoded': False
}

@patch('handler.boto3')
def test_invalid_json_input__responds_with_usage_msg(mock_boto3):
    mock_apigw = Mock()
    mock_boto3.client.return_value = mock_apigw
    event['body'] = 'Hello'

    defaultHandler(event, None)

    mock_apigw.post_to_connection.assert_called_once()
    msg = mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
    assert 'Send JSON object with program and input to run' in msg

@patch('handler.boto3')
def test_input_without_required_keys__responds_with_usage_msg(mock_boto3):
    mock_apigw = Mock()
    mock_boto3.client.return_value = mock_apigw
    event['body'] = json.dumps({'msg': 'hello'})

    defaultHandler(event, None)

    mock_apigw.post_to_connection.assert_called_once()
    msg = mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
    assert 'Send JSON object with program and input to run' in msg

@patch('handler.boto3')
def test_program_with_invalid_instruction__responds_with_error_message(mock_boto3):
    mock_apigw = Mock()
    mock_boto3.client.return_value = mock_apigw
    event['body'] = json.dumps({'program': [23], 'input': []})

    defaultHandler(event, None)

    mock_apigw.post_to_connection.assert_called_once()
    msg = mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
    assert 'Intcode program error' in msg

@patch('handler.boto3')
def test_program_with_invalid_mode__responds_with_error_message(mock_boto3):
    mock_apigw = Mock()
    mock_boto3.client.return_value = mock_apigw
    event['body'] = json.dumps({'program': [301], 'input': []})

    defaultHandler(event, None)

    mock_apigw.post_to_connection.assert_called_once()
    msg = mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
    assert 'Intcode program error' in msg

@patch('handler.boto3')
def test_valid_input__responds_with_program_output(mock_boto3):
    mock_apigw = Mock()
    mock_boto3.client.return_value = mock_apigw
    event['body'] = json.dumps({'program': [3,0,4,0,99], 'input': 42})

    defaultHandler(event, None)

    assert mock_apigw.post_to_connection.call_count == 2
    msg = mock_apigw.post_to_connection.call_args_list[0].kwargs['Data'].decode('utf8')
    assert msg == '42'

@patch('handler.boto3')
def test_valid_input__response_ends_with_program_completed_message(mock_boto3):
    mock_apigw = Mock()
    mock_boto3.client.return_value = mock_apigw
    event['body'] = json.dumps({'program': [3,0,4,0,99], 'input': 42})

    defaultHandler(event, None)

    msg = mock_apigw.post_to_connection.call_args_list[-1].kwargs['Data'].decode('utf8')
    assert msg == 'Program completed.'