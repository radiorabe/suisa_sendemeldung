FROM python:3-alpine@sha256:2a068b9442f61f4480306d44e3b166bfe3343761e9bd57c38f66302ebf28fd9e

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["python","-m","suisa_sendemeldung.suisa_sendemeldung"]
