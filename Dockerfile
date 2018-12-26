FROM python:3-alpine@sha256:f708ad35a86f079e860ecdd05e1da7844fd877b58238e7a9a588b2ca3b1534d8

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
