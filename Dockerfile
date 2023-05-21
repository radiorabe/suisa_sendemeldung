FROM ghcr.io/radiorabe/s2i-python:1.1.0 AS build

COPY ./ $HOME

RUN python3 setup.py bdist_wheel


FROM ghcr.io/radiorabe/python-minimal:1.0.7 AS app

COPY --from=build /opt/app-root/src/dist/*.whl /tmp/dist/

RUN    python3 -mpip --no-cache-dir install /tmp/dist/*.whl \
    && rm -rf /tmp/dist/

# make requests use os ca certs that contain the RaBe root CA
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

USER nobody

ENTRYPOINT ["suisa_sendemeldung"]
