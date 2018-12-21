FROM python:3-alpine@sha256:dcb518457b462cd2f1cec6202b5a44ddbb0ac50b6f024a06fe4671db5a119ff1

WORKDIR /src
COPY requirements.txt /src/
RUN ["pip","install","--no-cache-dir","-r","/src/requirements.txt"]
COPY . /src/

ENTRYPOINT ["/src/suisa_sendemeldung.py"]
