FROM python:3-alpine@sha256:434b6822c10cd1c7b483df5301f01f01309faa7a35c973dee22e43835ee00151

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
