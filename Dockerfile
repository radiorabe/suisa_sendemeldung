FROM python:3-alpine@sha256:55e23f0b3c5be7c21152290ee8fa7e8ed2ff99d9b8fdd76ea6df0344b4c8beeb

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
