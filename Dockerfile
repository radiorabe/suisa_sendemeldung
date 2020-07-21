FROM python:3-alpine@sha256:281d2acace02997c53218cd996af72e2e6fb304df032484d9ce2ce182b4f6757

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
