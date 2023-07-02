FROM ghcr.io/radiorabe/s2i-python:2.0.1 AS build

COPY --chown=1001:0 ./ /opt/app-root/src/

RUN python3.11 -m build .


FROM ghcr.io/radiorabe/python-minimal:2.0.1 AS app

COPY --from=build /opt/app-root/src/dist/*.whl /tmp/dist/

RUN    microdnf install -y \
         python3.11-pip \
    && python -mpip --no-cache-dir install /tmp/dist/*.whl \
    && microdnf remove -y \
         python3.11-pip \
         python3.11-setuptools \
    && microdnf clean all \
    && rm -rf /tmp/dist/

# make requests use os ca certs that contain the RaBe root CA
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

USER nobody

CMD ["suisa_sendemeldung"]
