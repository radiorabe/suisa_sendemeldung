FROM python:3-alpine@sha256:698816aee98b943878158ba950c83773c41ec98ff7117e5c9290e070957de246

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
