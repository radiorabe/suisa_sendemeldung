FROM python:3-alpine@sha256:159cd8d3c39964e54577fbfe8acab075913eade09ba3b7f2176c54c1dacfdc40

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
