# Intcode computer as a service

The intcode computer from Advent of Code 2019 (https://adventofcode.com/2019) as a service!

- Uses Websockets
- Running on AWS using Lambda, DynamoDB, API Gateway
- Built using Serverless Framework

## Usage
- Create virtual environment with required Python packages: `$ pipenv install`
- Load environment: `$ pipenv shell`
- Run unit tests: `$ pytest`
- Deploy (requires AWS account and Serverless Framework to be installed): `$ sls deploy`
- Check output from deploy command under "endpoints" and set environment variable: `$ export DEPLOYED_URL="wss://your-deployed-url"`
- Run E2E tests: `$ pytest test_e2e.py`

## Example session using wscat
```
$ wscat -c $DEPLOYED_URL
Connected (press CTRL+C to quit)
> hi? (send anything to start)
< Send JSON object with program and input to run, e.g.
{"action": "run", "program": [4,2,99], "input": []}
> {"action": "run", "program": [4,2,99], "input": []}
< 99
< Program completed.
> {"action": "run", "program": [3,0,3,0,4,0,99], "input": [17]}
< Additional input required. Send using JSON object, e.g.
{"action": "additional_input", "input": [5]}
> {"action": "additional_input", "input": [66]}
< 66
< Program completed.
>
```
