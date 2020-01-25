FROM python:3-alpine@sha256:cbfcea228e685aa3684f7a4e19be4805e3bf766f2158a4e3a54443cb608c1760

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
