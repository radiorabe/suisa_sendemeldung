FROM python:3-alpine@sha256:10950efa746cc607faaf66b970a4fe5649432d38228c483e257abd759b902d0f

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
