FROM python:3-alpine@sha256:08f24c8eb95d061404a181032f75558d1fcc083489496a0654f37ea3795f5e9a

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
