FROM python:3-alpine@sha256:f6cd6b6671abe5cb703fd02a0fe05ec5df17211f2a4de2a21967962eeb86758e

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
