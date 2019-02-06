FROM python:3-alpine@sha256:15dcc4754cf50b5d281b07af9f7b6eeedf0cb097d4fa3041c02dbe5846a118a1

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
