from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .models import *

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
        code.source_code = code.source_code.replace("\'", "\\\"" )
        code.source_code = code.source_code.replace("\"", "\\\"" )

        print('REQUEST IN PROCESS')
        docker_params = "docker run --rm -i python:3.8-slim "
        python_params = f'python3 -c \'{code.source_code}\' '
        sh_params = "sh -c "
        result = []
        total: int = len(code.shown_tests) + len(code.hidden_tests or [])
        passed = 0

        # Compile the code
        # completed_process = subprocess.run(docker_compile_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #
        # # Check if the compilation was successful
        # if completed_process.returncode != 0:
        #     print(completed_process.stderr.decode())
        #     return JSONResponse(
        #         status_code=400,
        #         content={ "status": "failed", "data": completed_process.stderr.decode()}
        #     )


        # Run shown tests
        for test in code.shown_tests:
            # Run each test with its input
            type_input = type(test.input)
            if type_input == list:
                test.output = str(test.output)
                input_values = "\"{ " + "; ".join(f"echo {num}" for num in test.input) + "; }"
                sh_params = "sh -c " + input_values

            else:
                # input_values = f'\" "{{ echo \'{test.input}\'; }} \"'
                input_values = f"\"echo '{test.input}' "
                sh_params = "sh -c " + input_values
            print(sh_params)


            exec_params = docker_params + sh_params + ' | ' + python_params + '"'
            print('$'+''.join(exec_params)+'$')
            completed_process = subprocess.run(exec_params, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Compare obtained result against expected output
            if completed_process.stdout.decode().strip() == test.output:
                passed += 1
                result.append({"status": "success", "input": test.input, "output": completed_process.stdout.decode().strip(), "expected": test.output })
            else:
                print('Error')
                print(completed_process.stderr)
                return JSONResponse(
                    status_code=403,
                    content={ "status": "failed", "total": total, "passed": passed, "test": { "input": test.input, "output": completed_process.stdout.decode().strip(), "expected": test.output} }
                )


        # Run hidden tests
        if code.hidden_tests:
            for test in code.hidden_tests:
                type_input = type(test.input)
                if type_input == list:
                    print('LIST')
                    sh_params = "{ " + "; ".join(f"echo {num}" for num in test.input) + "; }"

                else:
                    print('INT OR STR')
                    sh_params = f'{{ echo {test.input} }}'
                print(sh_params)

                exec_params = docker_params + [sh_params] + ['!'] + python_params
                # completed_process = subprocess.run(docker_exec_params, input=completed_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                completed_process = subprocess.run(exec_params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Compare obtained result against expected output
                if completed_process.stdout.decode().strip() == test.output.strip():
                    passed += 1
                else:
                    return JSONResponse(
                        status_code=402,
                        content={ "status": "failed", "total": total, "passed": passed, "test": { "input": test.input, "output": test.output, "result": completed_process.stdout.decode().strip()} }
                    )

        # Passed all test cases
        return JSONResponse(
            status_code=200,
            content={ "status": "success", "total": total, "passed": passed, "data": result }
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={ "status": "error", "data": "An error has ocurred" }
        )
