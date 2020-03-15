import json
import os

import pytest
import websockets

DEPLOYED_URL = os.getenv('DEPLOYED_URL')

@pytest.mark.asyncio
async def test_invalid_json_input__responds_with_usage_msg():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        body = 'hello'
        await websocket.send(body)

        assert 'Send JSON object with program and input to run' in await websocket.recv()

@pytest.mark.asyncio
async def test_valid_input__responds_with_program_output():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        body = json.dumps({'program': [3,0,4,0,99], 'input': 42})
        await websocket.send(body)

        assert await websocket.recv() == '42'
        assert await websocket.recv() == 'Program completed.'