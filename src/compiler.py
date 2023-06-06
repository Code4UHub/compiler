import subprocess

def format_code(code: str):
    code = code.replace("\'", "\\\"" )
    code = code.replace("\"", "\\\"" )
    return code


def format_input(input):
    sh_params = "sh -c "
    type_input = type(input)
    if type_input == list:
        input_values = "\"{ " + "; ".join(f"echo {num}" for num in input) + "; }"
        sh_params = "sh -c " + input_values
    else:
        input_values = f"\"echo '{input}' "
        sh_params = "sh -c " + input_values
    return sh_params


def format_output(output):
    type_output = type(output)
    if type_output == list:
        output = str(output)

    return output


def run_code(code: str, input) -> tuple:
    '''
    Runs a python code
        
        Parameters:
            code (str): Python code in a single string
            input (str): Input provided once file is running

        Returns:
            output (str): Output that the code prints
            error (str): Error given by the container
    '''
    try:
        sh_params = format_input(input)
        docker_params = "docker run --rm -i python:3.8-slim "
        python_params = f'python3 -c \'{code}\' '
        exec_params = docker_params + sh_params + ' | ' + python_params + '"'

        print('$'+''.join(exec_params)+'$')
        completed_process = subprocess.run(exec_params, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed_process.stderr:
            print('Compiler: AN ERROR HAS OCURREd')
            print(completed_process.stdout.decode().strip(), completed_process.stderr)
        return (completed_process.stdout.decode().strip(), completed_process.stderr.decode())
    except Exception as e:
        print('Compiler: Exception has ocurred')
        print(e)
        return('this', 'Compiler: exception triggered')

