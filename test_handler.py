import json
import unittest
from unittest.mock import patch, Mock

from handler import default_handler

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

class TestDefaultHandler(unittest.TestCase):
    def setUp(self):
        self.mock_apigw = Mock()
        self.mock_dynamodb = Mock()
        self.mocks = {
            'apigatewaymanagementapi': self.mock_apigw,
            'dynamodb': self.mock_dynamodb
        }

    def mock_for_service_selector(self, service_name, *args, **kwargs):
        return self.mocks[service_name]

    @patch('handler.boto3')
    def test_body_invalid_json__responds_with_usage_msg(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = 'Hello'

        default_handler(event, None)

        self.mock_apigw.post_to_connection.assert_called_once()
        msg = self.mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
        assert 'Send JSON object with program and input to run' in msg

    @patch('handler.boto3')
    def test_body_without_required_keys__responds_with_usage_msg(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = json.dumps({'msg': 'hello'})

        default_handler(event, None)

        self.mock_apigw.post_to_connection.assert_called_once()
        msg = self.mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
        assert 'Send JSON object with program and input to run' in msg

    @patch('handler.boto3')
    def test_program_with_invalid_instruction__responds_with_error_message(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = json.dumps({'program': [23], 'input': []})

        default_handler(event, None)

        self.mock_apigw.post_to_connection.assert_called_once()
        msg = self.mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
        assert 'Intcode program error' in msg
        assert 'Invalid instruction' in msg

    @patch('handler.boto3')
    def test_program_with_invalid_mode__responds_with_error_message(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = json.dumps({'program': [301], 'input': []})

        default_handler(event, None)

        self.mock_apigw.post_to_connection.assert_called_once()
        msg = self.mock_apigw.post_to_connection.call_args.kwargs['Data'].decode('utf8')
        assert 'Intcode program error' in msg
        assert 'Invalid mode' in msg

    @patch('handler.boto3')
    def test_valid_body__responds_with_program_output(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = json.dumps({'program': [3,0,4,0,99], 'input': [42]})

        default_handler(event, None)

        assert self.mock_apigw.post_to_connection.call_count == 2
        msg = self.mock_apigw.post_to_connection.call_args_list[0].kwargs['Data'].decode('utf8')
        assert msg == '42'

    @patch('handler.boto3')
    def test_valid_body__response_ends_with_program_completed_message(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = json.dumps({'program': [3,0,4,0,99], 'input': [42]})

        default_handler(event, None)

        msg = self.mock_apigw.post_to_connection.call_args_list[-1].kwargs['Data'].decode('utf8')
        assert msg == 'Program completed.'

    @patch('handler.boto3')
    def test_valid_body_missing_input__asks_for_input(self, mock_boto3):
        mock_boto3.client.side_effect = self.mock_for_service_selector
        event['body'] = json.dumps({'program': [3,0,3,0,99], 'input': [42]})

        default_handler(event, None)

        msg = self.mock_apigw.post_to_connection.call_args_list[0].kwargs['Data'].decode('utf8')
        assert 'Additional input required' in msg