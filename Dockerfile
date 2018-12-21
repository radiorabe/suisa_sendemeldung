FROM python:3-alpine@sha256:414a80a2deb1823a3248519a0dc300bb3ae59e9e2b660d730439e7b91551d3a4

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
