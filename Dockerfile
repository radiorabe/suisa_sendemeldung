FROM python:3-alpine@sha256:ce1b9f21341e78db3c71aa1b99876161a3bd2f7b428ddf35d54c59e1fad47107

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
