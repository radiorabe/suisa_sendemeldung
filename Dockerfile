FROM python:3-alpine@sha256:08b03b140633664ed4a55630de38f847d19059318c2473a5bff592d8a0b051d5

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["python","-m","suisa_sendemeldung.suisa_sendemeldung"]
