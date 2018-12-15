FROM python:3-alpine@sha256:abc2a66d8ce0ddf14b1d51d4c1fe83f21059fa1c4952c02116cb9fd8d5cfd5c4

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
