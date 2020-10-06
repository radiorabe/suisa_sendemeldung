FROM python:3-alpine@sha256:e4559a2e010d5d0f81c756c1df936e21a4daaad31bda583fb2f1d7e0fd314b1e

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
