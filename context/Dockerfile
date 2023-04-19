# Install Python.
FROM python:3.11-slim

# Install dependencies.
COPY requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip \
  && python -m pip install -r requirements.txt

WORKDIR /app
COPY /app /app 

ENTRYPOINT [ "python", "." ]
