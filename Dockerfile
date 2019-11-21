FROM python:3-alpine@sha256:3996a4b86240b6d41b57055cd7f626cbb15e2baef149b4fd841e04fec7308290

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
