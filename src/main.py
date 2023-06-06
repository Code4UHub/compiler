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
    return JSONResponse(
        status_code=422,
        content={"data": "Invalid request data"}
    )


@app.post("/run")
async def compile_and_run(code: Code):
    try:
        print('I AM HERE')
        source_code = format_code(code.source_code)

        result = []
        total: int = len(code.shown_tests) + len(code.hidden_tests or [])
        passed = 0

        # Run shown tests
        for test in code.shown_tests:
            # Run each test with its input
            code_input = format_output(test.input)
            expected_output = format_output(test.output)
            (code_output, code_error) = run_code(source_code, test.input)


            # Compare obtained result against expected output
            if code_output == expected_output:
                passed += 1
                result.append({"status": "success",
                               "input": code_input,
                               "output": code_output,
                               "expected": expected_output
                               })
            elif code_error:
                print('---ERROR IN CODE---')
                print(code_error)
                grade = math.ceil((passed / total) * 100)
                return JSONResponse(
                    status_code=400,
                    content={
                            "status": "error",
                            "total": total,
                            "passed": passed,
                            "grade": grade,
                            "message": code_error,
                            "test": result
                    }
                )

            else:
                print('OUTPUT DOESNT MATCH')
                result.append({"status": "failed",
                               "input": code_input,
                               "output": code_output,
                               "expected": expected_output
                               })


        # Run hidden tests
        # if code.hidden_tests:
        #     for test in code.hidden_tests:
        #         type_input = type(test.input)
        #         if type_input == list:
        #             print('LIST')
        #             sh_params = "{ " + "; ".join(f"echo {num}" for num in test.input) + "; }"
        #
        #         else:
        #             print('INT OR STR')
        #             sh_params = f'{{ echo {test.input} }}'
        #         print(sh_params)
        #
        #         exec_params = docker_params + sh_params + '|' + python_params
        #         # completed_process = subprocess.run(docker_exec_params, input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #         completed_process = subprocess.run(exec_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #
        #         # Compare obtained result against expected output
        #         if completed_process.stdout.decode().strip() == test.output.strip():
        #             passed += 1
        #         else:
        #             return JSONResponse(
        #                 status_code=402,
        #                 content={
        #                     "status": "failed",
        #                     "total": total,
        #                     "passed": passed,
        #                     "test": {
        #                         "input": test.input,
        #                         "output": test.output,
        #                         "result": completed_process.stdout.decode().strip()
        #                     }
        #                 }
        #             )

        # Passed all test cases
        grade = math.ceil((passed / total) * 100)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "total": total,
                "passed": passed,
                "grade": grade,
                "tests": result
            }
        )
    except Exception as e:
        print('EXCEPTION HAS TRIGGERED')
        print(e)
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

        total: int = len(code.shown_tests) + len(code.hidden_tests or [])
        passed = 0

        # Run shown tests
        for test in code.shown_tests:
            # Run each test with its input
            expected_output = format_output(test.output)
            (code_output, code_error) = run_code(source_code, test.input)


            # Compare obtained result against expected output
            if code_output == expected_output:
                passed += 1
            elif code_error:
                grade = math.ceil((passed / total) * 100)
                return JSONResponse(
                    status_code=400,
                    content={
                            "status": "error",
                            "total": total,
                            "passed": passed,
                            "grade": grade,
                            "message": code_error,
                    }
                )

        # Run hidden tests
        # if code.hidden_tests:
        #     for test in code.hidden_tests:
        #         type_input = type(test.input)
        #         if type_input == list:
        #             print('LIST')
        #             sh_params = "{ " + "; ".join(f"echo {num}" for num in test.input) + "; }"
        #
        #         else:
        #             print('INT OR STR')
        #             sh_params = f'{{ echo {test.input} }}'
        #         print(sh_params)
        #
        #         exec_params = docker_params + sh_params + '|' + python_params
        #         # completed_process = subprocess.run(docker_exec_params, input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #         completed_process = subprocess.run(exec_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #
        #         # Compare obtained result against expected output
        #         if completed_process.stdout.decode().strip() == test.output.strip():
        #             passed += 1
        #         else:
        #             return JSONResponse(
        #                 status_code=402,
        #                 content={
        #                     "status": "failed",
        #                     "total": total,
        #                     "passed": passed,
        #                     "test": {
        #                         "input": test.input,
        #                         "output": test.output,
        #                         "result": completed_process.stdout.decode().strip()
        #                     }
        #                 }
        #             )

        # Passed all test cases
        grade = math.ceil((passed / total) * 100)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "total": total,
                "passed": passed,
                "grade": grade,
            }
        )
    except Exception as e:
        print('EXCEPTION HAS TRIGGERED')
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "data": "An error has ocurred"
            }
        )
