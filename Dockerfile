FROM python:3-alpine@sha256:486782edd7f7363ffdc256fc952265a5cbe0a6e047a6a1ff51871d2cdb665351

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
