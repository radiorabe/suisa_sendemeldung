FROM python:3-alpine@sha256:906616c291ddc23201c675b880e7297e5528bbd352fcbdda8bf90546bb653e0a

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
