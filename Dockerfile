FROM python:3-alpine@sha256:c54bfea6195ec6c067b826c37a474308e93e3d9a1240811f9e01451599b28317

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
