# Install Python.
FROM python:3.11-slim

# Install dependencies.
COPY Pipfile /Pipfile
COPY Pipfile.lock /Pipfile.lock
RUN python -m pip install --upgrade pip \
  && python -m pip install pipenv \
  && python -m pipenv install

WORKDIR /app
COPY /app /app 

ENTRYPOINT [ "python", "." ]
