# FROM python:3.8-slim
FROM docker:latest

# Install Python 3.8 and pip
RUN apk update && \
    apk add --no-cache bash python3 python3-dev py3-pip

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

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

EXPOSE 9199
EXPOSE 9199

# Set the entry point command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9199"]
