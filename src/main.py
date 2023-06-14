import math
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .models import *
from .compiler import *



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
    print('Body wasnt valid')
    return JSONResponse(
        status_code=422,
        content={"data": "Invalid request data"}
    )

@app.get('/hello')
async def hello_world():
    print('App is up')
    return 'Hello world'

@app.post("/run")
async def compile_and_run(code: Code):
    try:
        print('I AM HERE')
        source_code = format_code(code.source_code)

        result = []
        total: int = len(code.tests) + len(code.hidden_tests or [])
        passed = 0

        # Run tests
        for test in code.tests:
            # Run each test with its input
            code_input = format_output(test.input)
            expected_output = format_output(test.output)
            (code_output, code_error) = run_code(source_code, test.input)


            # Compare obtained result against expected output
            if code_output == expected_output:
                passed += 1
                result.append({
                                "status": "success",
                                "input": code_input,
                                "output": code_output,
                                "expected": expected_output
                            })
            elif code_error:
                grade = math.ceil((passed / total) * 100)
                result.append({
                                "status": "error",
                                "input": code_input,
                                "expected": expected_output,
                                "output": code_error
                            })

            else:
                result.append({
                                "status": "failed",
                                "input": code_input,
                                "output": code_output,
                                "expected": expected_output
                            })



        # Passed all test cases
        grade = math.ceil((passed / total) * 100)
        print('Passed all test cases')
        return JSONResponse(
            status_code=200,
            content={
                # "status": "success",
                "total": total,
                "passed": passed,
                "score": grade,
                "tests": result
            }
        )
    except Exception as e:
        # print('EXCEPTION HAS TRIGGERED')
        # print(e)
        print('An error ocurred, idk!')
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "data": "An error has ocurred"
            }
        )

@app.post("/submit")
async def submit_code(code: Code):
    try:
        source_code = format_code(code.source_code)
        result = []

        total: int = len(code.tests) + len(code.hidden_tests or [])
        passed = 0

        # Run tests
        for test in code.tests:
            # Run each test with its input
            code_input = format_output(test.input)
            expected_output = format_output(test.output)
            (code_output, code_error) = run_code(source_code, test.input)


            # Compare obtained result against expected output
            if code_output == expected_output:
                passed += 1
                result.append({
                                "status": "success",
                                "input": code_input,
                                "output": code_output,
                                "expected": expected_output
                            })
            elif code_error:
                grade = math.ceil((passed / total) * 100)
                result.append({
                                "status": "error",
                                "input": code_input,
                                "output": code_error,
                                "expected": expected_output
                            })
            else:
                result.append({
                                "status": "failed",
                                "input": code_input,
                                "output": code_output,
                                "expected": expected_output
                            })


        # Passed all test cases
        grade = math.ceil((passed / total) * 100)
        status = 'sucess'
        if passed != total:
            status = 'failed'
        print('Passed all test cases')
        return JSONResponse(
            status_code=200,
            content={
                "status": status,
                "total": total,
                "passed": passed,
                "score": grade,
                "tests": result
            }
        )
    except Exception as e:
        # print('EXCEPTION HAS TRIGGERED')
        # print(e)
        print('An error ocurred, idk!')
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "data": "An error has ocurred"
            }
        )
