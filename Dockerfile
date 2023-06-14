FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy the Pipfile and Pipfile.lock
COPY Pipfile* ./

# Install app dependencies using pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the app's source code into the container
COPY . .

# Set the entry point command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "65535"]
# CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:65535"]
