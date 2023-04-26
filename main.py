from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import subprocess

class Test(BaseModel):
    input: str
    output: str

class Code(BaseModel):
    source_code: str
    shown_tests: List[Test]
    hidden_tests: List[Test]

class RunTest(BaseModel):
    input: str

class RunCode(BaseModel):
    source_code: str
    tests: List[RunTest]

app = FastAPI()

@app.post("/run")
async def run_code(run_code: RunCode):
    result = []
    total = len(run_code.tests)

    # Compile the code
    print('COMPILE CODE')
    completed_process = subprocess.run(["docker", "run", "--rm", "-i", "python:3.8-slim", "python3", "-c", run_code.source_code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print('CHECK IF COMPILED')
    # Check if the compilation was successful
    if completed_process.returncode != 0:
        return {"status": "error", "message": completed_process.stderr.decode()}

    # Run shown tests
    print('TEST CODE')
    for test in run_code.tests:
        completed_process = subprocess.run(["docker", "run", "--rm", "-i", "python:3.8-slim", "python3", "-c", run_code.source_code, test.input], input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result.append({"status": "success", "input": test.input, "result": completed_process.stdout.decode().strip()})

    # Passed all test cases
    return {"status": "success", "total": total, "data": result}


@app.post("/submit")
async def compile_and_run(code: Code):
    result = []
    total: int = len(code.shown_tests) + len(code.hidden_tests)

    # Compile the code
    completed_process = subprocess.run(["docker", "run", "--rm", "-i", "python:3.8-slim", "python3", "-c", code.source_code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the compilation was successful
    if completed_process.returncode != 0:
        return {"status": "error", "message": completed_process.stderr.decode()}

    # Run shown tests
    passed_test_cases = 0
    for test in code.shown_tests:
        completed_process = subprocess.run(["docker", "run", "--rm", "-i", "python:3.8-slim", "python3", "-c", code.source_code, test.input], input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the test passed or failed
        if completed_process.stdout.decode().strip() == test.output.strip():
            passed_test_cases += 1
            result.append({"status": "success", "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()})
        else:
            return {"status": "failed", "total": total, "passed": passed_test_cases, "test": { "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()}}


    # Run hidden tests
    for test in code.hidden_tests:
        completed_process = subprocess.run(["docker", "run", "--rm", "-i", "python:3.8-slim", "python3", "-c", code.source_code, test.input], input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the test passed or failed
        if completed_process.stdout.decode().strip() == test.output.strip():
            passed_test_cases += 1
        else:
            # result.append({"status": "failed", "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()})
            return {"status": "failed", "total": total, "passed": passed_test_cases, "test": { "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()}}

    # Passed all test cases
    return {"status": "success", "total": total, "passed": passed_test_cases, "data": result}
