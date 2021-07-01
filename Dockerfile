FROM python:3-alpine@sha256:3998e97aeeabfdeea57c6e05c7544c460ae158f24cc74371b7d4eca18fbc3171

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
