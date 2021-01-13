FROM python:3-alpine@sha256:0267b3631f06804da6b1a66c3b399e6335ed394d04d8c714b7a4dfa866c35337

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung/suisa_sendemeldung.py"]
