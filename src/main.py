from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from models import *

import subprocess



app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
# async def validation_exception_handler():
    return JSONResponse(
        status_code=422,
        content={"data": "Invalid request data"}
    )


@app.post("/submit")
async def run_code(code: Code):
    pass


@app.post("/run")
async def compile_and_run(code: Code):
    try:
        docker_compile_params = ["docker", "run", "--rm", "-i", "python:3.8-slim", "python3", "-c", code.source_code]
        result = []
        total: int = len(code.shown_tests) + len(code.hidden_tests)
        passed = 0

        # Compile the code
        completed_process = subprocess.run(docker_compile_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the compilation was successful
        if completed_process.returncode != 0:
            print(completed_process.stderr.decode())
            return JSONResponse(
                status_code=400,
                content={ "status": "failed", "data": completed_process.stderr.decode()}
            )


        # Run shown tests
        for test in code.shown_tests:
            # Run each test with its input
            docker_exec_params = docker_compile_params + [test.input]
            completed_process = subprocess.run(docker_exec_params, input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Compare obtained result against expected output
            if completed_process.stdout.decode().strip() == test.output.strip():
                passed += 1
                result.append({"status": "success", "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()})
            else:
                return JSONResponse(
                    status_code=400,
                    content={ "status": "failed", "total": total, "passed": passed, "test": { "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()} }
                )


        # Run hidden tests
        for test in code.hidden_tests:
            docker_exec_params = docker_compile_params + [test.input]
            completed_process = subprocess.run(docker_exec_params, input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Compare obtained result against expected output
            if completed_process.stdout.decode().strip() == test.output.strip():
                passed += 1
            else:
                return JSONResponse(
                    status_code=400,
                    content={ "status": "failed", "total": total, "passed": passed, "test": { "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()} }
                )

        # Passed all test cases
        return JSONResponse(
            status_code=200,
            content={ "status": "success", "total": total, "passed": passed, "data": result }
        )
    except:
        return JSONResponse(
            status_code=500,
            content={ "status": "error", "data": "An error has ocurred" }
        )
