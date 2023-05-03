# Install Python.
FROM python:3.11-slim

# Install git.
RUN apt-get -y update \
  && apt-get -y install git

# Install dependencies.
COPY Pipfile /Pipfile
COPY Pipfile.lock /Pipfile.lock
RUN python -m pip install --upgrade pip \
  && python -m pip install pipenv \
  && python -m pipenv install

# Start server.
COPY /app /app
WORKDIR /app
ENTRYPOINT [ "gunicorn", "api:app" ]
