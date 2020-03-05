import boto3


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
    message = f'Hello {connection_id}!'.encode('utf8')
    post_to_connection_response = gatewayapi.post_to_connection(Data=message, ConnectionId=connection_id)
    print('post_to_connection_response', post_to_connection_response)

    response = {
        "statusCode": 200,
        "body": "default"
    }

    return response