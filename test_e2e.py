import json
import os

import pytest
import websockets

DEPLOYED_URL = os.getenv('DEPLOYED_URL')

@pytest.mark.asyncio
async def test_body_invalid_json__responds_with_usage_msg():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        body = 'hello'

        await websocket.send(body)

        assert 'Send JSON object with program and input to run' in await websocket.recv()

@pytest.mark.asyncio
async def test_invalid_intcode_program__responds_with_program_error():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        body = json.dumps({'program': [23], 'input': []})

        await websocket.send(body)

        response = await websocket.recv()
        assert 'Intcode program error' in response

@pytest.mark.asyncio
async def test_additional_input_as_first_command__responds_with_usage_msg():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        additional_input = json.dumps({'action': 'additional_input', 'input': [43]})

        await websocket.send(additional_input)

        assert 'Send JSON object with program and input to run' in await websocket.recv()

@pytest.mark.asyncio
async def test_valid_body__responds_with_program_output_and_completed_message():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        body = json.dumps({'program': [3,0,4,0,99], 'input': [42]})

        await websocket.send(body)

        assert await websocket.recv() == '42'
        assert await websocket.recv() == 'Program completed.'

@pytest.mark.asyncio
async def test_valid_body_missing_input__finishes_after_providing_additional_input():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        body = json.dumps({'program': [3,0,3,0,4,0,99], 'input': [42]})
        additional_input = json.dumps({'action': 'additional_input', 'input': [43]})

        await websocket.send(body)
        assert 'Additional input required' in await websocket.recv()
        await websocket.send(additional_input)

        assert await websocket.recv() == '43'
        assert await websocket.recv() == 'Program completed.'

@pytest.mark.asyncio
async def test_additional_input_after_program_has_completed__responds_with_program_already_completed_message():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        # arrange
        body = json.dumps({'program': [3,0,3,0,4,0,99], 'input': [42]})
        additional_input = json.dumps({'action': 'additional_input', 'input': [43]})

        await websocket.send(body)
        await websocket.recv() # Additional input required
        await websocket.send(additional_input)
        await websocket.recv() # 43
        await websocket.recv() # Program completed.

        # act
        await websocket.send(additional_input)

        # assert
        assert 'Program already completed' in await websocket.recv()

@pytest.mark.asyncio
async def test_new_program_after_first_one_has_completed__runs_new_program():
    async with websockets.connect(DEPLOYED_URL) as websocket:
        # arrange
        body = json.dumps({'program': [3,0,4,0,99], 'input': [50]})

        await websocket.send(body)
        await websocket.recv() # 50
        await websocket.recv() # Program completed.

        # act
        body = json.dumps({'program': [4,2,99], 'input': []})
        await websocket.send(body)

        # assert
        assert await websocket.recv() == '99'
        assert await websocket.recv() == 'Program completed.'