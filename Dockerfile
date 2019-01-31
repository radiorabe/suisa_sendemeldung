FROM python:3-alpine@sha256:8fe3b17b88644d379ca7e0c724a82a595c8cfbe2b37e1d6d33e7bb5c435a8a29

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
