FROM alpine:latest

RUN apk add python3 py3-pip

RUN python3 -m pip install pytest

COPY src/ /usr/local/bin/api-class/src/
COPY tests/ /usr/local/bin/api-class/tests/


ENV PYTHONPATH "${PYTHONPATH}:/usr/local/bin/api-class/:"