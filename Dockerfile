FROM python:3-alpine@sha256:8412de90c7717917752ecb7f244087d4c7187622ac61051fdf4da95f8503e9cc

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
