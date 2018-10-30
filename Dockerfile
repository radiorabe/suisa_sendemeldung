FROM python:3-alpine

WORKDIR /src
COPY suisa_sendemeldung.py requirements.txt /src/
RUN ["pip","install","-r","/src/requirements.txt"]

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
