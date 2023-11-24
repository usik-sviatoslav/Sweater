FROM python:3.11


ARG PROD=False

ENV PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on


WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$PROD" == True && echo "--no-dev") --no-interaction --no-ansi

COPY . /code/
