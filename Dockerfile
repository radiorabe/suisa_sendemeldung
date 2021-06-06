FROM python:3-alpine@sha256:02311d686cd35b0f838854d6035c679acde2767a4fd09904e65355fbd9780f8a

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
