FROM python:3-alpine@sha256:bdd28cbb0c70c1360289bae9a7f7ed50d1e48200b8f950d20d27b3c91984b1bb

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
