FROM python:3-alpine@sha256:9546a3ee8e9a034ca85e537107f2a4756800fca1666823f3c9ae81c8251eb937

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
