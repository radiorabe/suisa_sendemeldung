FROM python:3-alpine@sha256:2a9b93b032246dabbec008c1527bd0ef31947e7fd351a200aec5a46eea68d776

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
