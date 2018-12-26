FROM python:3-alpine@sha256:f1da889b4ebc21abab10959f6785e165a9812b7059a066eceb6c49a0a5a2e319

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
